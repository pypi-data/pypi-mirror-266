"""
FreeGenius AI Plugin - send tweet

send a tweet to twitter

[FUNCTION_CALL]
"""

from freegenius import config
from freegenius.utils.shared_utils import SharedUtil
import urllib.parse

def send_tweet(function_args):
    message = function_args.get("message") # required
    config.stopSpinning()
    if message:
        SharedUtil.openURL(f"""https://twitter.com/intent/tweet?text={urllib.parse.quote(message)}""")
    return ""

functionSignature = {
    "examples": [
        "Send a tweet",
        "write twitter",
    ],
    "name": "send_tweet",
    "description": f'''Send a tweet to twitter''',
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message that is to be sent to twitter",
            },
        },
        "required": ["message"],
    },
}

config.addFunctionCall(signature=functionSignature, method=send_tweet)