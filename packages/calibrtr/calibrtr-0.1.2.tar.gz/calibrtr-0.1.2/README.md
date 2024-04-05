# Calibrtr-Client
Official Client library for calibrtr.com

## Python
### Installation
```bash
pip install calibrtr-client
```
### Usage
```python
from calibrtr import CalibrtrClient
from openai import OpenAI

openAiClient = OpenAI(api_key=["OPENAI_API_KEY"])

calibrtrClient = CalibrtrClient("[CALIBRTR_DEPLOYMENT_ID]", "[CALIBRTR_API_KEY]")

chat_completion = openAiClient.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "hello world",
        }
    ],
    model="gpt-3.5-turbo",
)

# TODO - get request and response tokens from chat_completion

calibrtrClient.logUsage("openai", 
                "gpt-3-turbo", 
                "[systemid]", 
                requestTokens,  # TODO - FIX ME
                responseTokens, # TODO - FIX ME
                feature="[featureName]",  # Optional
                user="[userhash]", # Optional
                request=request, # Optional
                response=response, # Optional
                )
```