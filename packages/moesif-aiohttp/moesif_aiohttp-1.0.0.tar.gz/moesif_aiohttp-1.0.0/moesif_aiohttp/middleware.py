from aiohttp.web import middleware
from datetime import datetime
from moesifapi.models import *
from moesifapi.parse_body import ParseBody
from moesifapi.moesif_api_client import MoesifAPIClient, Configuration
from moesifapi.config_manager import ConfigUpdateManager
from moesifapi.workers import BatchedWorkerPool, ConfigJobScheduler
from moesifapi.app_config import AppConfig
from moesifapi.api_helper import APIHelper
from moesifapi.update_companies import Company
from moesifapi.update_users import User
from .logger_helper import LoggerHelper
from .event_mapper import EventMapper
from aiohttp import web
import logging
import atexit
import random
import math
import aiohttp_sse

logger = logging.getLogger(__name__)

@middleware
class MoesifMiddleware:

    def __init__(self, settings):
        # Initialize the middleware with the configuration data
        self.settings = settings
        self.DEBUG = self.settings.get("DEBUG", False)
        self.parse_body = ParseBody()

        self.initialize_logger()
        self.validate_settings()

        self.initialize_counter()
        self.initialize_client()
        self.initialize_config()
        self.initialize_worker_pool()

        # graceful shutdown handlers
        atexit.register(self.worker_pool.stop)

    def initialize_logger(self):
        """Initialize logger mirroring the debug and stdout behavior of previous print statements for compatibility"""
        logging.basicConfig(
            level=logging.DEBUG if self.DEBUG else logging.INFO,
            format='%(asctime)s\t%(levelname)s\tPID: %(process)d\tThread: %(thread)d\t%(funcName)s\t%(message)s',
            handlers=[logging.StreamHandler()]
        )

    def validate_settings(self):
        if self.settings is None or not self.settings.get("APPLICATION_ID", None):
            raise Exception("Moesif Application ID is required in settings")

    def initialize_counter(self):
        self.dropped_events = 0
        self.logger_helper = LoggerHelper()
        self.event_mapper = EventMapper()

    def initialize_client(self):
        self.api_version = self.settings.get("API_VERSION")
        self.client = MoesifAPIClient(self.settings.get("APPLICATION_ID"))
        self.api_client = self.client.api

    def schedule_config_job(self):
        try:
            ConfigJobScheduler(self.DEBUG, self.config).schedule_background_job()
            self.is_config_job_scheduled = True
        except Exception as ex:
            self.is_config_job_scheduled = False
            if self.DEBUG:
                logger.info(f'Error while starting the config scheduler job in background: {str(ex)}')

    def initialize_config(self):
        Configuration.BASE_URI = self.settings.get("BASE_URI", "https://api.moesif.net")
        Configuration.version = "moesif_aiohttp/1.0.0"
        self.LOG_BODY = self.settings.get("LOG_BODY", True)

        self.app_config = AppConfig()
        self.config = ConfigUpdateManager(self.api_client, self.app_config, self.DEBUG)
        self.schedule_config_job()


    def initialize_worker_pool(self):
        # Create queues and threads which will batch and send events in the background
        self.worker_pool = BatchedWorkerPool(
            worker_count=self.settings.get("EVENT_WORKER_COUNT", 2),
            api_client=self.api_client,
            config=self.config,
            debug=self.DEBUG,
            max_queue_size=self.settings.get("EVENT_QUEUE_SIZE", 1000000),
            batch_size=self.settings.get("BATCH_SIZE", 100),
            timeout=self.settings.get("EVENT_BATCH_TIMEOUT", 2),
        )

    def prepare_response_content(self, body):
        response_content = None
        try:
            response_content = body[0].decode('utf-8')
        except Exception as ex:
            if self.DEBUG:
                logger.debug(f"Error while preparing the response content: {str(ex)}")
        return response_content

    async def __call__(self, request, handler):

        # Prepare Event Request Model
        event_request = await self.event_mapper.to_request(request, self.LOG_BODY)

        governed_response = {}
        if self.config.have_governance_rules():
            # we must fire these hooks early.
            user_id = self.logger_helper.get_user_id(self.settings, request, None, self.DEBUG)
            company_id = self.logger_helper.get_company_id(self.settings, request, None, self.DEBUG)
            governed_response = self.config.govern_request(event_request, user_id, company_id, event_request.body)

        blocked_by = None
        if 'blocked_by' in governed_response:
            # start response immediately, skip next step
            response_content = self.prepare_response_content(governed_response['body'])
            blocked_by = governed_response['blocked_by']
            response = web.Response(status=governed_response['status'], headers=governed_response['headers'], text=response_content)
        else:
            response = await handler(request)

        # Prepare Event Response Model
        event_response = self.event_mapper.to_response(response, self.LOG_BODY)

        # Add user, company, session_token, and metadata
        user_id = self.logger_helper.get_user_id(self.settings, request, response, self.DEBUG)
        company_id = self.logger_helper.get_company_id(self.settings, request, response, self.DEBUG)
        session_token = self.logger_helper.get_session_token(self.settings, request, response, self.DEBUG)
        metadata = self.logger_helper.get_metadata(self.settings, request, response, self.DEBUG)

        # Prepare Event Model
        event_model = self.event_mapper.to_event(event_request, event_response, user_id, company_id, session_token, metadata, blocked_by)

        # Check if needs to skip the event
        if self.logger_helper.should_skip(self.settings, request, response, self.DEBUG):
            logger.debug("Skipped Event using should_skip configuration option")
            return response

        # Mask Event Model
        event_model = self.logger_helper.mask_event(self.settings, event_model, self.DEBUG)

        # Sampling percentage
        event_sampling_percentage = self.config.get_sampling_percentage(event_model,user_id, company_id)

        # Add proportionate weight to the event for sampling percentage lower than 100
        event_model.weight = 1 if event_sampling_percentage == 0 else math.floor(100 / event_sampling_percentage)

        # if the event has a sample rate of less than 100, then we need to check if this event should be skipped and not sent to Moesif
        random_percentage = random.random() * 100
        if random_percentage >= event_sampling_percentage:
            logger.debug(f"Skipped Event due to sampling percentage: {str(event_sampling_percentage)}"
                         f" and random percentage: {str(random_percentage)}")
            return response

        try:
            # Add Event to the queue if able and count the dropped event if at capacity
            if self.worker_pool.add_event(event_model):
                logger.debug("Add Event to the queue")
                if self.DEBUG:
                    logger.debug(f"Event added to the queue: {APIHelper.json_serialize(event_model)}")
            else:
                self.dropped_events += 1
                logger.info(f"Dropped Event due to queue capacity drop_count: {str(self.dropped_events)}")
                if self.DEBUG:
                    logger.debug(f"Event dropped: {APIHelper.json_serialize(event_model)}")
        # add_event does not throw exceptions so this is unexepected
        except Exception as ex:
            logger.exception(f"Error while adding event to the queue: {str(ex)}")

        # Return response to the client
        return response

    def update_user(self, user_profile):
        User().update_user(user_profile, self.api_client, self.DEBUG)

    def update_users_batch(self, user_profiles):
        User().update_users_batch(user_profiles, self.api_client, self.DEBUG)

    def update_company(self, company_profile):
        Company().update_company(company_profile, self.api_client, self.DEBUG)

    def update_companies_batch(self, companies_profiles):
        Company().update_companies_batch(companies_profiles, self.api_client, self.DEBUG)
