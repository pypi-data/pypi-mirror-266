from django_silica.SilicaComponent import SilicaComponent
from django_silica.tests.SilicaTestCase import SilicaTestCase, SilicaTest


class Redirect(SilicaComponent):
    def redirect_me(self, path):
        self.redirect(path)

    def inline_template(self):
        return """
            <div class="p-5 border m-5">
                <p>I will be redirected!</p>
            </div>
        """


class RedirectTest(SilicaTestCase):
    def test_redirect_from_method(self):
        (
            SilicaTest(component=Redirect)
            .call("redirect_me", "/redirected")
            .assertJsCalled("_silicaRedirect", "/redirected")
        )
