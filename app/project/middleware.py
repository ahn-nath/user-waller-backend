import logging

from rest_framework_simplejwt.authentication import JWTAuthentication


class RequestResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django.request")

    def __call__(self, request):
        # Log request
        self.logger.debug(
            f"Request: {request.method} {request.get_full_path()}"
        )

        response = self.get_response(request)

        # Log response
        self.logger.debug(
            f"Response: {response.status_code} {response.reason_phrase}"
        )

        return response


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        token = request.COOKIES.get("access_token")
        if token:
            try:
                # Validate token
                jwt_auth = JWTAuthentication()
                jwt_auth.get_validated_token(token)
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
            except Exception as e:
                # If the token is invalid, ignore and move on without modifying the request
                logging.error(
                    f"JWTAuthenticationMiddleware on process_request: {e}"
                )
                pass
