from django.conf.urls import url, include
from . import views, catalog, custom
from dashboard.app import *

app_name = "APPNAME"

# Notes:
# 1. This merges the urls with the rest of the application URLs. Please be careful. 
# 2. app_urlpatterns is only for enrichapp.dashboard.custom app. All other apps ignore this field.
# 3. The reusable app and the app integrating the reusable app are different. Having both in the same urls.py will result in unexpected behavior

urlpatterns = []

# => Base that will be imported
APPNAME_urlpatterns = []

# Custom app
customspec = custom.get_spec()
register_app_instance(
    appmod="enrichapp.dashboard.custom",
    namespace="default",
    rootnamespace=app_name,
    urlpatterns=urlpatterns,
    spec=customspec,
    app_urlpatterns=[
        url(r'^[/]?$', views.index, name="index"),
    ]
)

catalogspec = catalog.get_spec()
register_app_instance(
    appmod="enrichapp.dashboard.catalog",
    namespace="catalog",
    rootnamespace=app_name,
    urlpatterns=urlpatterns,
    spec=catalogspec)

#from . import persona
#searchspec = persona.get_spec()
#register_app_instance(
#    appmod="enrichapp.dashboard.persona",
#    namespace="persona",
#    rootnamespace=app_name,
#    urlpatterns=urlpatterns,
#    spec=searchspec)
#
