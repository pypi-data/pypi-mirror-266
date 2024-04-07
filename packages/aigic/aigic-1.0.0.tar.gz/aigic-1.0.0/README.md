# AIGIC

AIGIC - Python sdk for AIGIC
A Python lib for AIGIC. It lets you run models from your Python code, and everything else you can do with AIGIC HTTP API.

- API version: 1.0
- Package version: 1.0.0

## Installation

### For [Python](https://www.python.org/)

#### npm

Install it from pip:

```shell
pip install aigic
```

## Getting Started

Please follow the [installation](#installation) instruction and execute the following JS code:

```python
from aigic import aigic

#get your api key or jwt token from https://console.aigic.ai
api_key = "my api key or jwt token"

aigic_instance = aigic.AIGIC(api_key)

data = {
    "input":{
        "seed": 36446545872,
        "width": 768,
        "height": 768,
        "prompt": "with smoke, half ice and half fire and ultra realistic in detail.wolf, typography, dark fantasy, wildlife photography, vibrant, cinematic and on a black background",
        "scheduler": "K_EULER",
        "num_outputs": 1,
        "guidance_scale": 9,
        "negative_prompt": "scary, cartoon, painting",
        "num_inference_steps": 25
    }
}

result = aigic_instance.prediction("/predictions/ai/ssd-1b",data)

print(result)

```

## API

All URIs are relative to *https://api.aigic.ai*

### Constructor

```javascript
aigic_instance = aigic.AIGIC(auth,host,headers)
```

name | type | Description
------------ | ------------- | -------------
*host* | string | The request host
*auth* | string | **Required**.You can choose either API key or JWT token for authentication.


## Docs

For more information, please visit the site *https://docs.aigic.ai*