from django.views.generic import TemplateView
from django.http import HttpResponse
from django.template import Context, Template


def create_test_view(inline_template_string, context_dict=None):
    """
    Dynamically creates a class-based view with the provided inline template string and context.

    :param inline_template_string: The template string to be rendered.
    :param context_dict: Optional dictionary to be used as context for rendering the template.
    :return: A class-based view dynamically generated.
    """
    if context_dict is None:
        context_dict = {}

    class DynamicTestView(TemplateView):
        def get(self, request, *args, **kwargs):
            context_dict['request'] = request

            template = Template("""
                {% load silica %}
                {% load silica_scripts %}
                {% silica_scripts %}    
            """ + inline_template_string)
            context = Context(context_dict)
            rendered_template = template.render(context)
            return HttpResponse(rendered_template)

    return DynamicTestView