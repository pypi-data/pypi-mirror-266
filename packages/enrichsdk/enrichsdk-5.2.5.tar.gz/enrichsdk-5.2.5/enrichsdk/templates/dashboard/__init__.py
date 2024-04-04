def get_urlpatterns(spec):
    from .urls import APPNAME_urlpatterns
    return APPNAME_urlpatterns

def get_config():
    from .apps import APPNAMEConfig
    return APPNAMEConfig
