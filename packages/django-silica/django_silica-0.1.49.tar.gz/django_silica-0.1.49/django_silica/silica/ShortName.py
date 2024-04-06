from django_silica.SilicaComponent import SilicaComponent


class ShortName(SilicaComponent):
    def inline_template(self):
        return """
            <div>
                I'm component called with short name!
            </div>
        """
