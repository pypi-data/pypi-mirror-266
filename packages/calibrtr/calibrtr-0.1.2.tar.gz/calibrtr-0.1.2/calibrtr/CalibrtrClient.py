import requests
import json

def serialize_completion(completion):
    return {
        "id": completion.id,
        "choices": [
            {
                "finish_reason": choice.finish_reason,
                "index": choice.index,
                "message": {
                    "content": choice.message.content,
                    "role": choice.message.role,
                    "function_call": {
                        "arguments": choice.message.function_call.arguments,
                        "name": choice.message.function_call.name
                    } if choice.message and choice.message.function_call else None
                } if choice.message else None
            } for choice in completion.choices
        ],
        "created": completion.created,
        "model": completion.model,
        "object": completion.object,
        "system_fingerprint": completion.system_fingerprint,
        "usage": {
            "completion_tokens": completion.usage.completion_tokens,
            "prompt_tokens": completion.usage.prompt_tokens,
            "total_tokens": completion.usage.total_tokens
        }
    }

class CalibrtrClient:

    def __init__(self, deployment_id, api_key, calibrtr_url="https://calibrtr.com/api/v1/deployments/{deploymentId}/logusage"):
        self.deployment_id = deployment_id
        self.api_key = api_key
        self.calibrtr_url = calibrtr_url

    def log_usage(self,
                  ai_provider,
                  ai_model,
                  system,
                  requestTokens,
                  responseTokens,
                  feature=None,
                  user=None,
                  request=None,
                    response=None):
        requestJson = None
        if request:
            try:
                requestJson = json.loads(json.dumps(request))
            except Exception as e:
                ()

        responseJson = None
        if response:
            try:
                responseJson = json.loads(json.dumps(response))
            except Exception as e:
                try:
                    responseJson = json.loads(json.dumps(serialize_completion(response)))
                except Exception as e:
                    ()


        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
            }
        data = {
            "aiProvider": ai_provider,
            "aiModel": ai_model,
            "system": system,
            "requestTokens": requestTokens,
            "responseTokens": responseTokens,
            "feature": feature,
            "user": user,
            "request": requestJson,
            "response": responseJson
        }
        url = self.calibrtr_url.format(deploymentId=self.deployment_id)
        try:
            response = requests.post(url, headers=headers, json=data)
            if(response.status_code != 200):
                print("Error while logging " + response.text)
        except requests.exceptions.RequestException as e:
            print(e)