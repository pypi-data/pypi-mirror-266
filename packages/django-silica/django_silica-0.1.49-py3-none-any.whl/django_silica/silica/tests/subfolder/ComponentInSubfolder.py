from django_silica.SilicaComponent import SilicaComponent


class ComponentInSubfolder(SilicaComponent):
    def inline_template(self):
        return """
            <div>
                I'm component in subfolder!
            </div>
        """
