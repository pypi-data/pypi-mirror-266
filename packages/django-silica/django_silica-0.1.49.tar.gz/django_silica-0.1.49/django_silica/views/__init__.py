from json import loads

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django_silica.SilicaComponent import SilicaComponent
from django_silica.errors import SetPropertyException


@require_POST
@csrf_exempt
def message(request, *args, **kwargs):
    """endpoint that processes dynamic updates to components"""

    request_body = loads(request.body)

    component_id = request_body.get("id")
    component_name = request_body.get("name")

    actions = request_body.get("actions")

    assert component_id, "Component id must be set"
    assert component_name, "Component name must be set"

    component_instance = SilicaComponent.create(
        component_id=component_id, component_name=component_name
    )

    component_instance.request = request

    # if actions is a List, for each action, execute
    if actions:
        for action in actions:
            if action["type"] == "set_property":
                name = action.get("name")
                value = action.get("value")

                try:
                    component_instance.set_property(name, value)
                except SetPropertyException as e:
                    return JsonResponse(
                        {
                            "error": f"Component {component_name}: {e}"
                        },
                        status=422,
                    )

                # call updated_[prop_name](value) hook
                # updated_hook_name = f"updated_{name}"
                # if hasattr(component_instance, updated_hook_name):
                #     getattr(component_instance, updated_hook_name)(value)
                #
                # # call updated(prop_name, value) hook
                # if hasattr(component_instance, "updated"):
                #     getattr(component_instance, "updated")(name, value)

            elif action["type"] == "call_method":
                method = getattr(component_instance, action["method_name"])
                method(*action.get("args", []), **action.get("kwargs", {}))
            elif action["type"] == "activate_lazy":
                component_instance.mount()
            elif action["type"] == "event":
                component_instance.receive_event(action["event_name"], action["payload"])

    component_instance.store_state()

    html = component_instance.render()

    snapshot = component_instance.create_snapshot()

    return JsonResponse(
        {
            "html": html,
            "id": component_id,
            "snapshot": snapshot,
        }
    )

