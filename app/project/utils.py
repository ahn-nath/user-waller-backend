from drf_yasg.generators import OpenAPISchemaGenerator


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        """Generate a :class:`.Swagger` object with custom tags"""

        swagger = super().get_schema(request, public)

        # Set the base path based on the title of the Swagger document
        title = swagger.info.title
        if title == "Wallet API":
            swagger.base_path = "/wallet/"

        if title == "Auth API":
            swagger.base_path = "/auth/"

        if title == "KYC API":
            swagger.base_path = "/users/kyc/"

        if title == "Users API":
            swagger.base_path = "/"

        # TODO: ?finish
        # swagger.tags = [
        #     {
        #         "name": "Auth",
        #         "description": """
        #     """,
        #         "externalDocs": {"description": "(Auth flow diagram)", "url": "#"},
        #     },
        #     {"name": "users", "description": "everything about your users"},
        #     {"name": "wallet", "description": "everything about wallets"},
        # ]

        return swagger
