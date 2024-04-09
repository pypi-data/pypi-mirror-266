import logging
import os
import json
import base64

logger = logging.getLogger(__name__)

class LoggerHelper:

    def __init__(self):
        pass

    @classmethod
    def transform_token(cls, token):
        if not isinstance(token, str):
            token = token.decode('utf-8')
        return token

    @classmethod
    def fetch_token(cls, token, token_type):
        return token.split(token_type, 1)[1].strip()

    @classmethod
    def split_token(cls, token):
        return token.split('.')

    def parse_authorization_header(self, token, field, debug):
        try:
            # Fix the padding issue before decoding
            token += '=' * (-len(token) % 4)
            # Decode the payload
            base64_decode = base64.b64decode(token)
            # Transform token to string to be compatible with Python 2 and 3
            base64_decode = self.transform_token(base64_decode)
            # Convert the payload to json
            json_decode = json.loads(base64_decode)
            # Convert keys to lowercase
            json_decode = {k.lower(): v for k, v in json_decode.items()}
            # Check if field is present in the body
            if field in json_decode:
                # Fetch user Id
                return str(json_decode[field])
        except Exception as e:
            if debug:
                logger.info(f"Error while parsing authorization header to fetch user id: {str(e)}")
        return None

    def get_user_id(self, settings, request, response, debug):
        username = None
        try:
            identify_user = settings.get("IDENTIFY_USER")
            if identify_user is not None:
                try:
                    username = identify_user(request, response)
                except Exception as e:
                    logger.warning(f"Exception in identify_user function, please check your identify_user method: {str(e)}")
            if not username:
                # Parse request headers
                request_headers = dict([(k.lower(), v) for k, v in request.headers.items()])
                # Fetch the auth header name from the config
                auth_header_names = settings.get('AUTHORIZATION_HEADER_NAME', 'authorization').lower()
                # Split authorization header name by comma
                auth_header_names = [x.strip() for x in auth_header_names.split(',')]
                # Fetch the header name available in the request header
                token = None
                for auth_name in auth_header_names:
                    # Check if the auth header name in request headers
                    if auth_name in request_headers:
                        # Fetch the token from the request headers
                        token = request_headers[auth_name]
                        # Split the token by comma
                        token = [x.strip() for x in token.split(',')]
                        # Fetch the first available header
                        if len(token) >= 1:
                            token = token[0]
                        else:
                            token = None
                        break
                # Fetch the field from the config
                field = settings.get('AUTHORIZATION_USER_ID_FIELD', 'sub').lower()
                # Check if token is not None
                if token:
                    # Check if token is of type Bearer
                    if 'Bearer' in token:
                        # Fetch the bearer token
                        token = self.fetch_token(token, 'Bearer')
                        # Split the bearer token by dot(.)
                        split_token = self.split_token(token)
                        # Check if payload is not None
                        if len(split_token) >= 3 and split_token[1]:
                            # Parse and set user Id
                            username = self.parse_authorization_header(split_token[1], field, debug)
                    # Check if token is of type Basic
                    elif 'Basic' in token:
                        # Fetch the basic token
                        token = self.fetch_token(token, 'Basic')
                        # Decode the token
                        decoded_token = base64.b64decode(token)
                        # Transform token to string to be compatible with Python 2 and 3
                        decoded_token = self.transform_token(decoded_token)
                        # Fetch the username and set the user Id
                        username = decoded_token.split(':', 1)[0].strip()
                    # Check if token is of user-defined custom type
                    else:
                        # Split the token by dot(.)
                        split_token = self.split_token(token)
                        # Check if payload is not None
                        if len(split_token) > 1 and split_token[1]:
                            # Parse and set user Id
                            username = self.parse_authorization_header(split_token[1], field, debug)
                        else:
                            # Parse and set user Id
                            username = self.parse_authorization_header(token, field, debug)
        except Exception as e:
            if debug:
                logger.info(f"can not execute identify_user function, please check moesif settings: {str(e)}")
        return username


    @classmethod
    def get_company_id(cls, settings, request, response, debug):
        company_id = None
        try:
            identify_company = settings.get("IDENTIFY_COMPANY")
            if identify_company is not None:
                company_id = identify_company(request, response)
        except Exception as e:
            if debug:
                logger.info(f"can not execute identify_company function, please check moesif settings: {str(e)}")
        return company_id

    @classmethod
    def get_session_token(cls, settings, request, response, debug):
        session_token = None
        try:
            get_session = settings.get("GET_SESSION_TOKEN")
            if get_session is not None:
                session_token = get_session(request, response)
        except Exception as e:
            if debug:
                logger.info(f"can not execute get_session function, please check moesif settings: {str(e)}")
        return session_token

    @classmethod
    def get_metadata(cls, settings, request, response, debug):
        metadata = None
        try:
            get_meta = settings.get("GET_METADATA")
            if get_meta is not None:
                metadata = get_meta(request, response)
        except Exception as e:
            if debug:
                logger.info(f"can not execute GET_METADATA function, please check moesif settings: {str(e)}")
        return metadata

    @classmethod
    def should_skip(cls, settings, request, response, debug):
        try:
            skip_proc = settings.get("SKIP")
            if skip_proc is not None:
                return skip_proc(request, response)
            else:
                return False
        except Exception as e:
            if debug:
                logger.info(f"error trying to execute skip function: {str(e)}")
            return False

    @classmethod
    def mask_event(cls, settings, event_model, debug):
        try:
            mask_event_model = settings.get("MASK_EVENT_MODEL")
            if mask_event_model is not None:
                return mask_event_model(event_model)
        except Exception as e:
            if debug:
                logger.info(f"Can not execute MASK_EVENT_MODEL function. Please check moesif settings: {str(e)}")
        return event_model

    