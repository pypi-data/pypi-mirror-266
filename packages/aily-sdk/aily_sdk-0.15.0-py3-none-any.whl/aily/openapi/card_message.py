import json

from aily.openapi import OpenAPIClient


class CardMessageResult:
    def __init__(self, result):
        self.code = result['code']
        self.msg = result['msg']

        self.message_id = None
        if 'data' in result:
            self.message_id = result['data']['message_id']


class CardMessageClient(OpenAPIClient):
    def send_message(self, template_id, template_version_name, template_variable, receive_id):
        url = "https://open.larkoffice.com/open-apis/im/v1/messages"
        params = {"receive_id_type": "open_id"}
        body = self.make_card_message(template_id, template_version_name, template_variable, receive_id=receive_id)
        return CardMessageResult(self.post(url, data=body, query=params))

    def reply_message(self, template_id, template_version_name, template_variable, message_id):
        url = f'https://open.larkoffice.com/open-apis/im/v1/messages/{message_id}/reply'
        body = self.make_card_message(template_id, template_version_name, template_variable, message_id=message_id)
        return CardMessageResult(self.post(url, data=body))

    @staticmethod
    def make_card_message(template_id, template_version_name, template_variable, receive_id=None,
                          message_id=None):
        api_json = {
            "msg_type": "interactive",
        }
        if message_id is None or message_id == '':
            api_json['receive_id'] = receive_id
            api_json['receive_id_type'] = 'open_id'

        message = {'type': 'template', 'data': {
            'template_id': template_id, 'template_version_name': template_version_name,
            'template_variable': template_variable}}
        api_json['content'] = json.dumps(message)

        return api_json
