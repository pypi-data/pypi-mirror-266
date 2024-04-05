# Flask binary queue processor
## Aim
The aim of this project is to provide a simple backend processor that receives
binary data and stores it in a queue that it's processed in a background
thread.

On receiving the request the server verifies that it is compliant with request
data, returning a 204 when successful and 404 when not. 

In background, the server analyzes files, processes it and when processed send
result to a callback url supplied in request.

## Request data
The application must receive a request which contains:

* **callback**, the url where information should be returned.
* **file**, the binary file that contains the information.

## Response data (callback request)
The callback url receives a JSON object and, optionally, a file that contains
the processed output.

JSON object has the following format:
* **success** Whether the processing has been successful or not.
* **error** If success is falsy, the error message
* **data** If success is true, the text data,

The file object is returned in a file parameter, using a multipart/form-data
response.

Note that only one of data or file is returned.

## Using it
`app.py` file shows a pretty simple use case, in this case the `process`
function just log the filename of the input returning a `true` and a sample
text data. Just modify `app.py` in order to support your use case.

## To do
In fact there are may things to improve over this simple scenario, for example:
* Support a persistent queue
* Support for multiple consumer, not only one processor
* In case that callback call fails, due to origin fallen, it should be nice to
  retry the callback action after some minutes.

## Dependencies
This package depends on `flask` and `requests` don't forget to add those dependencies to your installation

```pip install flask```

```pip install requests```

## Running tests
Just execute `python -m unittest discover test`

## Running
For development or testing purposes just execute `flask run`

