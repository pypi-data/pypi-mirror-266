#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple webhooks
"""

import json
from string import Template
from urllib import request
import urllib.error

# --- Http post with json payload ----

class webhook_error(Exception):
    """
    Webhook error exception, raised by the ```webhook_post``` class in case of errors.

    """
    pass

class webhook_post:
    """
    Send webhook messages.

    This is basically just a JSON formatted HTTP Post request, looking like:

    ```
    {
        text: "<message body>"
    }
    ```

    """
    def __init__(self, a_sURL):
        """
        Constructor.

        Args:
            a_sURL: The URL where the HTTP Post should be sent to (str)

        """
        # Not fancy, but should work for MS Teams
        self._sURL = a_sURL

    # Fill in template with values from dictionary and post it
    def post_template(self, a_sMsgTemplateFile, a_tMsgTemplateDict):
        """
        Send webhook HTTP Post. Instead of expecting the message as a complete text, this function allows to supply a dictionary and a template file.

        Args:
            a_sMsgTemplateFile: Path of a template file (str)
            a_tMsgTemplateDict: Dictionary holding the keys/values for the template. All occurences of every ```$<key>``` in the template file will be replaced with the respective value from the dict. (dict)

        Raises:
            webhook_error on any filesystem related error.
            any urllib exceptions during post requests
        """
        try:
            with open(a_sMsgTemplateFile, 'r') as f:
                tpl = Template(f.read())
                msg = tpl.safe_substitute(a_tMsgTemplateDict)
                self.post( msg)
        except OSError as e:
               raise webhook_error(f'Could not read template file {f}: {str(e)}')

    # Simple html formatting: bold caption, unmodified body
    def post_formatted(self, a_sCaption, a_sBody):
        """
        Send webhook HTTP Post. This sends a simple HTML formatted message.

        Args:
            a_sCaption: 'Caption' will be bold and on top of the message body (str)
            a_sBody: Main message body with no special formatting beneath the 'caption' (str)

        Raises:
            any exception that *post()* raises
        """
        sMsg = f'<h2><strong>{a_sCaption}</strong></h2><br>{a_sBody}'
        self.post(sMsg)

    # Base function, post raw message
    def post(self, a_sMsg):
        """
        Send webhook HTTP Post. This is the base function which just sends an unmodified 'raw' string.

        Args:
            a_sMsg: Messages to send (str)

        Raises:
            webhook_error on any error
        """
        post = request.Request(url=self._sURL, method="POST")
        post.add_header(key="Content-Type", val="application/json")
        try:
            with request.urlopen(url = post, data = json.dumps({"text": a_sMsg}).encode() ) as response:
                if response.status != 200:
                    raise webhook_error("Error response from receiver: " + response.reason)
        except urllib.error.URLError as e:
            raise webhook_error("Could not send HTTP POST: " + str(e))
