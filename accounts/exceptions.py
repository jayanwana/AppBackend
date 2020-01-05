from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def base_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # check that a ValidationError exception is raised
    if isinstance(exc, ValidationError):
        # Including custom error message for validation error
        if response.data.get("email", None):
            response.data = response.data["email"][0]
        elif response.data.get("full_name", None):
            response.data = response.data['full_name'][0]
        elif response.data.get("password", None):
            response.data = response.data["password"][0]

    return response
