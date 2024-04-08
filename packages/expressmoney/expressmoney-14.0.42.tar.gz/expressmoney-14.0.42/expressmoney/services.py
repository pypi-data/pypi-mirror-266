import json
import os

import boto3
import requests
from django.core.exceptions import ValidationError
from requests.auth import HTTPBasicAuth
from rest_framework import status


class RuSmsService:
    _url = 'https://omnichannel.mts.ru/http-api/v1/messages'

    def __init__(self):
        self._login, self._password = os.getenv('MTS_SMS').split('||')

    def send(self, phonenumber, sender, message):
        response = requests.post(self._url,
                                 json=self._get_payload(phonenumber, sender, message),
                                 auth=HTTPBasicAuth(self._login, self._password),
                                 timeout=(30, 30)
                                 )
        if not status.is_success(response.status_code):
            raise ValidationError(response.text)
        result = self._get_result(response.json().get("messages")[0].get("internal_id"))
        self._handle_errors(result)

    def _get_result(self, internal_id):
        try:
            response_info = requests.post(url=f"{self._url}/info",
                                          json={"int_ids": [internal_id]},
                                          auth=HTTPBasicAuth(self._login, self._password), )
            return response_info.json().get('events_info')[0].get('events_info')[0]
        except (IndexError, TypeError, IOError):
            pass

    @staticmethod
    def _get_payload(phonenumber, sender, message):
        msisdn = f'{phonenumber.country_code}{phonenumber.national_number}'
        payload = {
            "messages": [
                {
                    "content": {
                        "short_text": message
                    },
                    "from": {
                        "sms_address": sender
                    },
                    "to": [
                        {
                            "msisdn": msisdn
                        }
                    ]
                }
            ]
        }
        return payload

    @staticmethod
    def _handle_errors(result):
        if not result:
            return
        internal_errors = result.get('internal_errors')
        if not internal_errors:
            return result
        elif 10802 in internal_errors:
            raise ValidationError('phonenumber_format_error')
        elif 10803 in internal_errors:
            raise ValidationError('unsupported_code_country')
        elif 10904 in internal_errors:
            raise ValidationError('phonenumber_blacklist')
        elif 10100 in internal_errors:
            raise ValidationError('incorrect_sender')
        else:
            raise ValidationError(internal_errors)


class YandexObjectService:
    _bucket = 'expressmoney'
    _filename = None

    def __init__(self):
        self._s3 = boto3.session.Session().client(service_name='s3', endpoint_url='https://storage.yandexcloud.net')

    def generate_key(self, filename):
        self._filename = filename
        prepared_form_fields = self._s3.generate_presigned_post(Bucket=self._bucket,
                                                                Key=f'files/{self._filename}',
                                                                Conditions=[["starts-with", "$key", "files"], ],
                                                                ExpiresIn=60 * 60)
        return json.dumps(prepared_form_fields)
