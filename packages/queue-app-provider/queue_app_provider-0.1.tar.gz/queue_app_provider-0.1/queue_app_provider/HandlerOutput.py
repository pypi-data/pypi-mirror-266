import logging

import requests


# This class is a holder for all information regarding the processing
# of a handler, a handler is the function accountable of working on
# a image or binary data to create proper output.
#
# It's just a wrapper of a `success` a `text` or a `file` if the
# output of processor is a file.
#
# This information is used within the `notify` method (which receives a
# callback function) to report source of the translation of the
# issue.
#
# Created by: David Rodríguez Alfayate
# Version: 1.0
class HandlerOutput:
    def __init__(self, success: bool, text: str, file=""):
        self.success = success
        self.file = file
        self.text = text

    # As stated above the notify method receives the callback url, and according this
    # object internal state it sends the proper response to the origin.
    def notify(self, callback: str):
        try:
            # On fail
            if not self.success:
                requests.post(callback, json={"success": False, "error": self.text})
                return
            # On success, but a file
            if self.file:
                requests.post(callback, json={"success": True}, files={'file': open(self.file, 'rb')})
                return
            # Normal text
            requests.post(callback, json={"success": True, "data": self.text})
        except requests.exceptions.RequestException:
            # In a more complex scenario we should, perhaps, enqueue this callback response, expecting
            # than in the near future the remote server could be up again. For this simple example,
            # we are just ignoring the request, logging the error event
            logging.exception('There was an error sending callback')
            return
