from django_silica.SilicaComponent import SilicaComponent
from django_silica.tests.SilicaTestCase import SilicaTestCase, SilicaTest


class JsCalls(SilicaComponent):
    def set_js_call(self):
        self.js_call("alert", "hi")

    def inline_template(self):
        return "<div>testing</div>"


class TestJsCalls(SilicaTestCase):
    def test_js_is_called(self):
        (
            SilicaTest(component=JsCalls)
            .call("set_js_call")
            .assertJsCalled("alert", "hi")
        )
