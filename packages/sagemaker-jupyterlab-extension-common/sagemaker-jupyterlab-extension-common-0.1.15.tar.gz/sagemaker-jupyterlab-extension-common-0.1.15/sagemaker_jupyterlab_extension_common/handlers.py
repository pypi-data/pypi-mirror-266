import json
import traceback
from jupyter_events import EventLogger

from tornado import web
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join
from dateutil.parser import isoparse
from jsonschema.exceptions import ValidationError

from .constants import CONTEXT_INJECT_PLACEHOLDER
from .logging.logging_utils import SchemaDocument
from .logging.logging_utils import create_ui_eventlogger
from .util.app_metadata import (
    get_region_name,
    get_stage,
    get_aws_account_id,
    get_space_name,
)


class JupterLabUILogHandler(JupyterHandler):
    """Handle event log requests emitted by Studio JupyterLab UI"""

    eventlog_instance = None

    def get_eventlogger(self) -> EventLogger:
        if not JupterLabUILogHandler.eventlog_instance:
            """ "Create a StudioEventLog with the correct schemas"""
            schema_documents = [
                SchemaDocument.JupyterLabOperation,
                SchemaDocument.JupyterLabPerformanceMetrics,
            ]
            JupterLabUILogHandler.eventlog_instance = create_ui_eventlogger(
                schema_documents
            )
        return JupterLabUILogHandler.eventlog_instance

    def inject_log_context(self, event_record):
        if event_record and "Context" in event_record:
            event_context = event_record.get("Context")
            # Inject account id
            if event_context.get("AccountId", None) == CONTEXT_INJECT_PLACEHOLDER:
                event_context["AccountId"] = get_aws_account_id()
            if event_context.get("SpaceName", None) == CONTEXT_INJECT_PLACEHOLDER:
                event_context["SpaceName"] = get_space_name()

    @web.authenticated
    async def post(self):
        try:
            body = self.get_json_body()
            if not "events" in body:
                self.log.error("No events provided")
                self.set_status(400)
                self.finish(json.dumps({"errorMessage": "No events provided"}))
            events = body.get("events", [])
            for event in events:
                schema = event.get("schema")
                event_record = event.get("body")
                publish_time = event.get("publishTime")
                self.inject_log_context(event_record)
                timestamp = None
                if publish_time is not None:
                    timestamp = isoparse(event.get("publishTime"))
                self.get_eventlogger().emit(
                    schema_id=schema, data=event_record, timestamp_override=timestamp
                )
            self.set_status(204)
        except ValidationError as error:
            self.log.error("Invalid request {} {}".format(body, traceback.format_exc()))
            self.set_status(400)
            self.finish(json.dumps({"errorMessage": "Invalid request or wrong input"}))
        except Exception as error:
            self.log.error("Internal Service Error: {}".format(traceback.format_exc()))
            self.set_status(500)
            self.finish(json.dumps({"errorMessage": str(error)}))


class SageMakerContextHandler(JupyterHandler):
    @web.authenticated
    async def get(self):
        region = get_region_name()
        stage = get_stage()
        spaceName = get_space_name()
        self.set_status(200)
        self.finish(
            json.dumps({"region": region, "stage": stage, "spaceName": spaceName})
        )


def build_url(web_app, endpoint):
    base_url = web_app.settings["base_url"]
    return url_path_join(base_url, endpoint)


def register_handlers(nbapp):
    web_app = nbapp.web_app
    host_pattern = ".*$"
    handlers = [
        (
            build_url(web_app, r"/aws/sagemaker/api/eventlog"),
            JupterLabUILogHandler,
        ),
        (
            build_url(web_app, r"/aws/sagemaker/api/context"),
            SageMakerContextHandler,
        ),
    ]
    web_app.add_handlers(host_pattern, handlers)
