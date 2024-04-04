from enrichsdk.app.utils import EnrichAppConfig

class APPNAMEConfig(EnrichAppConfig):
    name = 'APPNAME'
    verbose_name = "APPDESC"
    description = f"APPDESC"
    category = "APPNAME"
    tags = []
    status = "alpha"
    enable = True
    filename = __file__
    multiple = False
    composition = True

    @classmethod
    def get_readme(cls):
        return """APPDESC"""
