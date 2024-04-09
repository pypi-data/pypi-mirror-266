from collections import defaultdict
import datetime, json, logging, time

from arkhos.http import HttpResponse, JsonResponse, render, render_static

from arkhos import _global


def base_handler(event, context=""):
    start_time = time.time()

    request = Request(event)
    response = {}

    try:
        if request.path.startswith("/static/"):
            response = render_static(request.path)
        else:
            user_handler = get_user_handler()
            response = user_handler(request)

        if isinstance(response, (HttpResponse, JsonResponse)):
            response = response.serialize()
    except:
        logging.exception("User handler error")
        response = JsonResponse({"error": "500 Server Error"}, status=500).serialize()

    finally:
        end_time = time.time()
        duration = end_time - start_time
        """
        log("%s HTTP %s request" %(_global.APP_NAME, request["method"]),
            status=response.status, # bigtodo: user set status
             type=request["method"]) # todo: headers
        log_flush()
        """
        response["arkhos_duration"] = {
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
        }

    return response


def get_user_handler():
    """This returns the user's handler"""

    if __name__ == "__main__":
        pass  # script, running in lambda
    else:  # module, running locally
        import os, sys

        sys.path.append(os.getcwd())

    from main import arkhos_handler

    return arkhos_handler


class Request:
    """Represents a request"""

    def __init__(self, lambda_event):
        self.method = lambda_event.get("method")
        self.headers = lambda_event.get("headers", {})
        self.GET = lambda_event.get("GET", {})
        self.POST = lambda_event.get("POST", {})
        self.parsed_json = False

        # todo
        self.path = lambda_event.get("path")  # todo: cron

    @property
    def json(self):
        """Parse the request body. This will throw an error if request.body
        isn't valid json"""
        self.parsed_json = self.parsed_json or json.loads(self.POST)
        return self.parsed_json
