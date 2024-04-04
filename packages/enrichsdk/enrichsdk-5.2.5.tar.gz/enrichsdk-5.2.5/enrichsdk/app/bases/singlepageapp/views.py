import os
import re
import json
import traceback
import logging
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
import base64

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

from django.http import QueryDict
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db import models
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages
from django.urls import reverse, resolve
from django.conf.urls import url, include

import s3fs
import gcsfs

from users.decorators import log_activity
from dashboard.lib import log_app_activity

from enrichsdk.utils import SafeEncoder
from enrichapp.spec import validate_spec as default_validate_spec, fill_action_gaps
from enrichsdk.lib import get_credentials_by_name
from enrichsdk.utils import SafeEncoder
from enrichsdk.datasets import Doodle
from enrichsdk.lib import get_default_from_email
from enrichsdk.lib.integration import send_html_email

logger= logging.getLogger('app')


###############################################
# Main class
###############################################
class AppBase():
    """
    A shareable view across apps
    """

    def __init__(self):
        self.name = "singlepageapp"
        self.verbose_name = "Single Page App"
        self.category = "singlepageapp"
        self.templates = {
            'index': f'enrichapp/singlepageapp/index.html',
            'helper': f'enrichapp/singlepageapp/helper.html',
            'workflow_index': f'enrichapp/policyapp/workflow_index.html',
        }

    def __str__(self):
        return f"[{self.name}] {self.verbose_name}"

    def get_readme(self):
        return """This is a generic single page app"""

    def get_template(self, spec, name):
        return spec.get('templates',{}).get(name, self.templates.get(name, "Unable to find template"))

    def get_model(self, spec, name):

        from enrichapp.dashboard.globalapp import lib as globallib

        if (('models' in spec) and (name in spec['models'])):
            return spec['models'][name]

        return globallib.get_model(name)

    def get_form(self, spec, name):

        from enrichapp.dashboard.globalapp import lib as globallib

        if (('forms' in spec) and (name in spec['forms'])):
            return spec['forms'][name]

        return globallib.get_form(name)

    def validate_spec(self, spec):

        fill_action_gaps(spec, context={ })

        errors = default_validate_spec(spec)
        if len(errors) > 0:
            return len(errors) == 0, errors

        return len(errors) == 0, errors

    def check_prerequisites(self, request, spec):

        valid, errors = self.validate_spec(spec)
        if not valid:
            error = "Invalid specification"
            messages.error(request, error)
            msg = "Errors: " + json.dumps(errors, indent=4, cls=SafeEncoder)
            msg += "Spec:\n" + json.dumps(spec,  indent=4, cls=SafeEncoder)

            logger.error(error,
                         extra={
                             'transform': 'Dashboard',
                             'data': msg
                         })
            return valid, HttpResponseRedirect(reverse('dashboard:application_index'))

        return valid, None

    def get_urlpatterns(self):
        urlpatterns = [
            url('^workflows/action[/]?$', self.workflow_action, name="workflow_action"),
            url('^[/]?$', self.index, name="index"),
        ]

        return urlpatterns

    ################################################################
    # Workflow Management
    ################################################################
    def get_supported_actions(self, request, spec):
        return ['Email']

    def take_action(self, request, spec, data, target):

        r = resolve(request.path)

        detailurl = request.build_absolute_uri(reverse(r.namespace + ":index")) + "?" + request.GET.urlencode()

        try:
            if target.nature == "Email":

                """{
                    "emails": [
                       "pingali@scribbledata.io"
                     ]
                }"""

                policy = target.policy
                if (('emails' not in policy) and (not isinstance(target.policy['emails'], list))):
                    return JsonResponse({
                        'status': 'failure',
                        'message': "Email service not configured correct. Please contact the admin"
                    })

                user = request.user
                fullname = f"{user.first_name} {user.last_name}".strip()
                if len(fullname) == 0:
                    fullname = user.username

                sender = fullname + "<" + get_default_from_email() +">"
                receivers = policy['emails']
                subject = f"{spec['name']} - Sharing Observation"
                content = f"<p>{data['message']}</p>"
                content += f"<p>You can find the full details at <a href='{detailurl}'>{spec['name']}</a> app."
                if (('data' in data) and (len(data) > 0)):
                    content += "Here is quick context:</p>"
                    content += "<p>" + data['data'] + "</p>"

                msg = MIMEMultipart()
                msg.attach(MIMEText(content, "html"))
                send_html_email(content=content,
                                sender=sender,
                                receivers=receivers,
                                subject=subject)

                return JsonResponse({
                    'status': 'success',
                    'message': "Email sent successfully"
                })

            return JsonResponse({
                'status': "failure",
                "message": f"Workflow service not configured correctly. Please contact admin"
            })

        except Exception as e:
            traceback.print_exc()
            logger.exception("Unable to send email")
            return JsonResponse({
                'status': "failure",
                "message": f"{target.nature} message action could not be taken. {str(e)}"
            })

    @log_activity("workflow_action", nature="application")
    def workflow_action(self, request, spec):
        """
        Show the workflows for the given data
        """

        from dashboard.models import AppActionTarget

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']

        data = request.POST.dict()

        try:
            try:
                target = AppActionTarget.objects.get(pk=data['actionid'])
            except:
                raise Exception("Internal error. Missing or invalid action id")

            # messages.success(request, "Processed the post")
            status = "success"

            # Make this happen...
            status = self.take_action(request, spec, data, target)

        except Exception as e:
            return JsonResponse({
                'status': 'failure',
                'message': f"Failed to trigger action. {str(e)}"
            })

        return status


    ################################################################
    # Data Access
    ################################################################
    def get_fs_handle(self, cred):
        """
        Get s3/gcs filesystem handle..
        """
        cred = get_credentials_by_name(cred)
        nature = cred['nature']
        if nature not in ['s3', 'gcs']:
            raise Exception(f"Unknown credentials: {nature}")

        if nature == 's3':
            config_kwargs={
                'signature_version': 's3v4'
            }

            if 'region' in cred:
                config_kwargs['region_name'] = cred['region']

            fshandle = s3fs.S3FileSystem(
                key    = cred['access_key'],
                secret = cred['secret_key'],
                config_kwargs=config_kwargs,
                use_listings_cache=False
            )
        else:
            fshandle = gcsfs.GCSFileSystem(
                token=cred['keyfile']
            )

        return fshandle

    def get_data(self, request, spec):

        try:
            data = {
                "test": "This is test data"
            }

        except:
            logger.exception(f"Error in accessing {spec['name']} results")

        return data

    @log_activity("app_index", nature="application")
    def index(self, request, spec):

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']

        template = self.get_template(spec, 'index')
        helper = self.get_template(spec, 'helper')

        try:
            data = self.get_data(request, spec)
        except:
            logger.exception("Unable to read data")
            messages.error(request, "Unable to read data. See log")
            return HttpResponseRedirect(reverse('dashboard:application_index'))

        return render(request,
                      template,
                      {
                          'app': self,
                          'spec': spec,
                          'usecase': usecase,
                          'basenamespace': r.namespace,
                          'data': data,
                          'helper': helper
                      })


    def get_router(self):

        from ninja import Router, Query, Schema

        router = Router()

        # Nothing to do...
        return router
