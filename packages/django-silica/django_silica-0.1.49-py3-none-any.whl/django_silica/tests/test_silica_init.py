import time

from django.test import override_settings
from django.urls import path

from django_silica.SilicaComponent import SilicaComponent
from django_silica.tests.SilicaTestCase import SilicaBrowserTestCase
from django_silica.tests.utils import create_test_view
from django_silica.urls import urlpatterns as silica_urlpatterns


TestView = create_test_view(f"""{{% silica '{__name__}.SilicaInitComponent' %}}""")

urlpatterns = silica_urlpatterns + [
    path("silica-init", TestView.as_view()),
]


class SilicaInitComponent(SilicaComponent):
    light_property = "hello I take no time to load"
    mounted_light_property: str = None
    heavy_data_property: str = ''

    def mount(self):
        self.mounted_light_property = "I'm also quite light"

    def slow_method(self):
        time.sleep(0.4)
        self.heavy_data_property = "I am heavy data"

    def inline_template(self):
        return """
            <div silica:init="slow_method">
                <style>.red { color: red }</style>
                <style>.hidden { display: none }</style>
            
                {{ light_property }}
                {{ mounted_light_property }}
                {{ heavy_data_property }}       

                <div id="loading-message" silica:loading>I am loading no matter what mate</div>
                <div id="initiating-message" silica:loading.init>I am an initiating message</div>    
                <div id="proceeding-message" silica:loading.proceeding>I am a proceeding message</div>
                <div id="class-message" silica:loading.class="red">I am red whilst loading</div>
                
                <div id="loading-hidden" silica:loading.hidden>I am hidden whilst loading</div> 
                <div id="initiating-hidden" silica:loading.init.hidden>I am hidden whilst initiating</div> 
            </div>
        """


@override_settings(ROOT_URLCONF=__name__)
class SilicaInitTestCase(SilicaBrowserTestCase):

    def test_init_functionality(self):
        self.selenium.get(self.live_server_url + '/silica-init')

        self.assertHtmlContains("hello I take no time to load")
        self.assertHtmlContains("I'm also quite light")
        self.assertHtmlNotContains("I am heavy data")

        time.sleep(0.5)

        self.assertHtmlContains("I am heavy data")

    def test_initiating_loader(self):
        self.selenium.get(self.live_server_url + '/silica-init')

        self.assertIdIsVisible('loading-message')
        self.assertIdIsVisible('initiating-message')
        self.assertIdIsVisible('class-message')
        self.assertHtmlContains(' class="red"')
        self.assertIdIsNotVisible('proceeding-message')

        time.sleep(0.5)

        self.assertIdIsNotVisible('loading-message')
        self.assertIdIsNotVisible('initiating-message')
        self.assertIdIsVisible('class-message')
        self.assertHtmlNotContains(' class="red"')
        
    


