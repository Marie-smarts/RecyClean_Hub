import sys

class RedirectDebugger:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if 300 <= response.status_code < 400:
            location = response.get('Location', 'unknown')
            print(f"\n>>> REDIRECT: {request.path} -> {location} (status={response.status_code})", file=sys.stderr)
        return response