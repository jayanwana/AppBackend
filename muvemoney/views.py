from django.views.generic import TemplateView
# Create your views here.
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers


class SwaggerSchemaView(APIView):
    permission_classes = [IsAdminUser]
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
    ]

    def get(self, request):
        generator = SchemaGenerator()
        schema = generator.get_schema(request=request)

        return Response(schema)


class HomePage(TemplateView):
    template_name = 'index.html'


class ThanksPage(TemplateView):
    template_name = 'thanks.html'
