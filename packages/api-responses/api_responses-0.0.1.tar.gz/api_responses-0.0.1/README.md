# api-reponses

Api Responses is a python package useful for give an structure to your Http Response.

## Installing

Installing and update using pip:

```
$ pip install -U api_response
```

## A simple example

```
from api_responses.responses import ResponseOk as Ok
from flask import Flask
import secrets
import string

app = Flask(__name__)

@app.route("/generate-password", methods=['GET'])
def generate_simple_password():
    """Endpoint generate default password long=16 chars"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ""
    for _ in range(16):
        password += secrets.choice(characters)

    return Ok.with_results(
            code=0,
            message="Sucessful",
            result=password
    )
```
