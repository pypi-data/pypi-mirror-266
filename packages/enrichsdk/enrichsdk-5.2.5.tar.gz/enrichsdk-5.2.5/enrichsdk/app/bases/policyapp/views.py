import os
import re
import json
import traceback
import logging
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
import base64

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
from enrichsdk.lib.integration import send_html_email
from enrichsdk.lib import get_default_from_email

from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage

import pandas as pd
from pretty_html_table import build_table

logger= logging.getLogger('app')


###############################################
# Main class
###############################################
class AppBase():
    """
    A shareable view across apps
    """

    def __init__(self):
        self.name = "outliers"
        self.verbose_name = "Outliers"
        self.category = "outliers"
        self.templates = {
            'policy_index': f'enrichapp/policyapp/policy_index.html',
            'policy_add': f'enrichapp/policyapp/policy_add.html',
            'policy_select_dataset': f'enrichapp/policyapp/policy_select_dataset.html',
            'policy_select_columns': f'enrichapp/policyapp/policy_select_columns.html',
            'policy_select_columns_helper': f'enrichapp/policyapp/policy_select_columns_helper.html',
            'result_index': f'enrichapp/policyapp/result_index.html',
            'result_detail': f'enrichapp/policyapp/result_detail.html',
            'workflow_index': f'enrichapp/policyapp/workflow_index.html',

        }
        self.select_columns_post_spec = {
            'list_columns': []
        }

    def __str__(self):
        return f"[{self.name}] {self.verbose_name}"

    def get_readme(self):
        return """This is a generic policy app"""

    def get_template(self, spec, name):
        return spec.get('templates',{}).get(name, self.templates[name])

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

        if 'namespace' not in spec:
            errors.append(f"namespace should be specified")

        if (('doodle' not in spec) or
            ((not isinstance(spec['doodle'], dict)) and (not callable(spec['doodle'])))):
            errors.append(f"Doodle metadata server is not specified")

        if ('data' not in spec):
            errors.append(f"Data section must be mentioned")
        else:
            missing = [col for col in ['type', 'cred', 'root'] if col not in spec['data']]
            if len(missing) > 0:
                errors.append(f"Missing data elements: {','.join(missing)}")

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
            url('^[/]?$', self.index, name="index"),
            url('^configurations[/]?$', self.policy_index, name="policy_index"),
            url('^configurations/add[/]?$', self.policy_add, name="policy_add"),
            url('^configurations/(?P<policy_id>[0-9]+)/toggle[/]?$', self.policy_toggle, name="policy_toggle"),
            url('^configurations/select/dataset[/]?$', self.policy_select_dataset, name="policy_select_dataset"),
            url('^configurations/select/columns[/]?$', self.policy_select_columns, name="policy_select_columns"),
            url('^results[/]?$', self.result_index, name="result_index"),
            url('^results/detail[/]?$', self.result_detail, name="result_detail"),
            url('^workflows/action[/]?$', self.workflow_action, name="workflow_action"),
            url('^workflows[/]?$', self.workflow_index, name="workflow_index")
        ]

        return urlpatterns

    @log_activity("app_index", nature="application")
    def index(self, request, spec):

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        return HttpResponseRedirect(reverse(r.namespace + ":policy_index"))

    @log_activity("app_policy_index", nature="application")
    def policy_index(self, request, spec):
        """
        Policy index...
        """

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']

        template = self.get_template(spec, 'policy_index')

        namespace = spec.get('namespace', 'default')
        try:
            namepace = spec['namespace']
            PolicyModel    = self.get_model(spec, 'app_policy')
            policies = PolicyModel.objects\
                                  .filter(appname=self.name, namespace=namespace)\
                                  .order_by("-id")

        except:
            logger.exception(f"Unable to get {self.name} policies. Please see server log")
            #return HttpResponseRedirect(reverse(r.namespace + ":index"))

        return render(request,
                      template,
                      {
                          'app': self,
                          'spec': spec,
                          'usecase': usecase,
                          'basenamespace': r.namespace,
                          'policies': policies
                      })


    @log_activity("app_policy_toggle", nature="application")
    def policy_toggle(self, request, spec, policy_id):
        """
        Activate/Deactivate policy
        """

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']


        namespace      = spec.get('namespace', 'default')
        PolicyModel    = self.get_model(spec, 'app_policy')
        policies       = PolicyModel.objects.filter(pk=policy_id, appname=self.name, namespace=namespace)
        if policies.count() == 0:
            messages.error(request, "No policy found")
            return HttpResponseRedirect(reverse(r.namespace + ":policy_index"))

        policy = policies[0]
        policy.active = not policy.active
        policy.save()
        messages.success(request, "Policy updated")
        return HttpResponseRedirect(reverse(r.namespace + ":policy_index"))

    @log_activity("app_policy_select_dataset", nature="application")
    def policy_select_dataset(self, request, spec):
        """
        Select datasets to process
        """
        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']

        template = self.get_template(spec, 'policy_select_dataset')
        cred = spec['doodle']
        if callable(cred):
            cred = cred(spec)

        doodle = Doodle(cred)

        # Collect the sources
        sources = doodle.list_sources()

        return render(request,
                      template,
                      {
                          'app': self,
                          'spec': spec,
                          'usecase': usecase,
                          'basenamespace': r.namespace,
                          'sources': sources
                      })

    def validate_policy_config(self, request, spec, config):
        """
        Validate the config generated by the backend
        """
        return len(config) > 0

    def policy_generate_config(self, request, spec):
        """
        Process the select columns form
        """

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        source_id = request.GET.get('source_id', None)
        if ((source_id is None) or (request.method != "POST")):
            logger.error("Missing source id or not a post")
            return HttpResponseRedirect(reverse(r.namespace + ":policy_select_dataset"))

        config = request.GET.dict()
        config.update(request.POST.dict())
        listcols = self.select_columns_post_spec['list_columns']
        for col in listcols:
            config[col] = request.POST.getlist(col)

        # Cleanup
        config.pop('csrfmiddlewaretoken',None)

        valid = self.validate_policy_config(request, spec, config)

        return valid, config

    @log_activity("app_policy_select_columns", nature="application")
    def policy_select_columns(self, request, spec):
        """
        Select columns
        """
        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']
        template = self.get_template(spec, 'policy_select_columns')

        # Now access the metadata server..
        source_id = request.GET.get('source_id', None)
        if source_id is None:
            logger.error("Missing source id")
            return HttpResponseRedirect(reverse(r.namespace + ":policy_select_dataset"))
        source_version = request.GET.get('source_version', 'v1')

        # Handle the post from selection...
        if request.method == "POST":
            valid, config = self.policy_generate_config(request, spec)
            if not valid:
                # Errors got incorporated in the validate function..
                messages.error(request, "Invalid selection")
                return HttpResponseRedirect(reverse(r.namespace + ":policy_select_columns") + f"?source_id={source_id}&source_version={source_version}")
            try:
                config = json.dumps(config)
                return HttpResponseRedirect(reverse(r.namespace + ":policy_add") + f"?config={config}")
            except Exception as e:
                logger.exception("Error while redirecting to policy add")
                messages.error(request, "Error while adding a policy")
                return HttpResponseRedirect(reverse(r.namespace + ":policy_select_columns") + f"?source_id={source_id}&source_version={source_version}")


        # Collect the sources
        cred = spec['doodle']
        if callable(cred):
            cred = cred(spec)
        doodle = Doodle(cred)

        source = doodle.get_source(source_id)
        features = doodle.list_features(source_id=source['id'])

        # Now render
        return render(request,
                      template,
                      {
                          'app': self,
                          'spec': spec,
                          'usecase': usecase,
                          'basenamespace': r.namespace,
                          'select_columns_helper': self.get_template(spec, 'policy_select_columns_helper'),
                          'source': source,
                          'columns': features
                  })


    @log_activity("app_policy_add", nature="application")
    def policy_add(self, request, spec):
        """
        Add a policy
        """

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']
        template = self.get_template(spec, 'policy_add')

        # => Get models
        namespace   = spec.get('namespace','default')
        PolicyModel = self.get_model(spec, 'app_policy')
        PolicyForm  = self.get_form(spec,  'app_policy')

        config = request.GET.get('config', '{}')
        config = json.loads(config)

        if request.method != "POST":

            initial = {
                "config": config,
            }

            form = PolicyForm(initial=initial)

            return render(request,
                          template,
                          {
                              'app': self,
                              'spec': spec,
                              'usecase': usecase,
                              'basenamespace': r.namespace,
                              'form': form
                          })


        form = PolicyForm(request.POST)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.appname = self.name
            policy.namespace = namespace
            policy.created_by = request.user
            policy.modified_by = request.user
            policy.active = True
            policy.save()

            log_app_activity(request, self.name, spec, "policy added", policy.desc)

            messages.success(request, 'Policy {} saved!'.format(policy.name))
            return HttpResponseRedirect(reverse(r.namespace + ":policy_index"))


        return render(request,
                      template,
                      {
                          'app': self,
                          'spec': spec,
                          'usecase': usecase,
                          'basenamespace': r.namespace,
                          'form': form
                      })

    ####################################################3
    # Result
    ####################################################3
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

    def get_result_list(self, request, spec, policies):

        try:
            available = {}

            data = spec['data']
            handle = self.get_fs_handle(data['cred'])

            appname = self.name
            namespace = spec['namespace']

            root = os.path.join(data['root'], appname, namespace)

            fallback = spec.get('fallback',False)
            if fallback:
                if not handle.exists(root):
                    messages.warning(request, "Result root directory is missing. choosing alternative")
                    namespaces = handle.ls(os.path.join(data['root'], appname))
                    if len(namespaces) == 0:
                        return []
                    root = namespaces[0]


            # What should I be looking at?
            relevant_configurations = [p.name for p in policies if ((p.appname == self.name) &
                                                                    (p.namespace == namespace))]

            # available paths
            # Look for the subset within the namespace
            paths = handle.find(root, maxdepth=2, withdirs=True)
            confmap = {}
            for p in paths:
                p = p.replace(root+ "/", "").split("/")
                if len(p) != 2:
                    continue
                confname, dt = p
                if confname not in confmap:
                    confmap[confname] = {
                        'dates': []
                    }
                confmap[confname]['dates'].append(dt)

            for confname in list(confmap.keys()):
                confmap[confname]['latest'] = max(confmap[confname]['dates'])

            available = {c: detail for c, detail in confmap.items() if ((c in relevant_configurations) or True)}

            if hasattr(handle, 'close'):
                handle.close()

        except:
            #traceback.print_exc()
            logger.exception(f"Error in accessing {spec['name']} results")

        return available

    def get_one_result_path(self, request, spec, policy, handle, path):

        # Read the s3/gcs file. Check if this is a string
        content = json.load(handle.open(path))
        if isinstance(content, str):
            content = json.loads(content)

        return content

    def get_result(self, request, spec, policy):
        """
        Get data from s3 and other places
        """
        try:

            data = spec['data']
            handle = self.get_fs_handle(data['cred'])

            appname = self.name
            namespace = spec['namespace']

            root = os.path.join(data['root'], appname, namespace)

            # may be different from policy.name
            name = request.GET.get('name')

            fallback = spec.get('fallback',False)
            if fallback:
                if not handle.exists(root):
                    messages.warning(request, "Result root directory is missing. choosing alternative")
                    namespaces = handle.ls(os.path.join(data['root'], appname))
                    root = namespaces[0]

            names = [os.path.basename(n) for n in handle.ls(root)]
            if name not in names:
                raise Exception(f"Could not find {name}")

            dates = sorted(handle.ls(os.path.join(root, name)), reverse=True)
            if len(dates) == 0:
                return None, None

            paths = sorted(handle.ls(dates[0]), reverse=True)
            if len(paths) == 0:
                return None

            content = None
            paths = [p for p in paths if not p.endswith('metadata.json')]
            for p in paths:
                try:
                    content = self.get_one_result_path(request,
                                                       spec, policy,
                                                       handle, p)
                    return p, content
                except:
                    #traceback.print_exc()
                    continue

            if hasattr(handle, 'close'):
                handle.close()

        except:
            logger.exception(f"Error in accessing {policy.name} results")

        return None, None

    @log_activity("app_result_index", nature="application")
    def result_index(self, request, spec):
        """
        Show the available results
        """

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']

        template = self.get_template(spec, 'result_index')

        namespace = spec.get('namespace', 'default')
        try:
            namepace = spec['namespace']
            PolicyModel    = self.get_model(spec, 'app_policy')
            policies = PolicyModel.objects\
                                  .filter(appname=self.name,
                                          namespace=namespace)\
                                  .order_by("-id")
        except Exception as e:
            messages.error(request, f"Error! {e}")
            logger.exception(f"Unable to get {namespace} configurations. Please see server log")
            return HttpResponseRedirect(reverse(r.namespace + ":policy_index"))

        available = self.get_result_list(request, spec, policies)

        return render(request,
                      template,
                      {
                          'app': self,
                          'spec': spec,
                          'usecase': usecase,
                          'basenamespace': r.namespace,
                          'policies': policies,
                          'available': available
                      })

    @log_activity("app_result_detail", nature="application")
    def result_detail(self, request, spec):
        """
        Show the available results
        """
        from dashboard.models import AppActionTarget

        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        fallback = spec.get('fallback', False)
        usecase = spec['usecase']

        template = self.get_template(spec, 'result_detail')

        name = request.GET.get('name', None)
        if name is None:
            messages.error(request, "Missing configuration")
            return HttpResponseRedirect(reverse(r.namespace + ":result_index"))

        try:
            namespace      = spec['namespace']
            PolicyModel    = self.get_model(spec, 'app_policy')
            policy         = PolicyModel.objects\
                                          .get(appname=self.name,
                                               namespace=namespace,
                                               name=name,
                                               active=True
                                          )
        except Exception as e:
            logger.exception(f"Unable to get configuration for {name}")
            if not fallback:
                messages.error(request, f"Unable to get configuration for {name}")
                return HttpResponseRedirect(reverse(r.namespace + ":result_index"))

            messages.warning(request, f"Unable to get configuration for {name}")
            try:
                policy = PolicyModel.objects.filter(appname=self.name,namespace=namespace, active=True).first()
            except:
                messages.warning(request, f"No policy defined for fallback")
                return HttpResponseRedirect(reverse(r.namespace + ":result_index"))

        path, data = self.get_result(request, spec, policy)
        if data is None:
            messages.error(request, f"Unable to get data for configuration {name}")
            logger.exception(f"Unable to get data for configuration {name}")
            return HttpResponseRedirect(reverse(r.namespace + ":result_index"))

        # Workflow targets
        supported_actions = self.get_supported_actions(request, spec, policy)
        targets = AppActionTarget.objects.filter(nature__in=supported_actions)

        return render(request,
                      template,
                      {
                          'app': self,
                          'spec': spec,
                          'usecase': usecase,
                          'basenamespace': r.namespace,
                          'name': name,
                          'policy': policy,
                          'data': data,
                          'path': path,
                          'targets': targets
                      })

    ################################################################
    # Workflow Management
    ################################################################
    def get_supported_actions(self, request, spec, policy):
        return ['Email']

    def take_action(self, request, spec, name, data, target):

        r = resolve(request.path)
        detailurl = request.build_absolute_uri(reverse(r.namespace + ":result_detail")) + f"?name={name}"

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
                content += f"<p>You can find the full details at <a href='{detailurl}'>{spec['name']}</a> page. Here is quick context:</p>"
                table = json.loads(data['data'])
                s = pd.Series(table).reset_index()
                s.columns = ['Attribute', 'Value']
                content += build_table(s,
                                       'blue_light',
                                       font_size='small',
                                       font_family='Roboto, sans-serif')

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

        name = request.GET.get('name', None)
        if name is None:
            logger.exception("Missing name of the result")
            return HttpResponseRedirect(reverse(r.namespace + ":result_index"))

        data = request.POST.dict()

        try:
            try:
                target = AppActionTarget.objects.get(pk=data['actionid'])
            except:
                raise Exception("Internal error. Missing or invalid action id")

            messages.success(request, "Processed the post")
            status = "success"

            # Make this happen...
            status = self.take_action(request, spec, name, data, target)

        except Exception as e:
            return JsonResponse({
                'status': 'failure',
                'message': f"Failed to trigger action. {str(e)}"
            })

        return status

    @log_activity("workflow_index", nature="application")
    def workflow_index(self, request, spec):
        """
        Show the workflows for the given data
        """

        from dashboard.models import AppActionTarget


        r = resolve(request.path)

        valid, redirect = self.check_prerequisites(request, spec)
        if not valid:
            return redirect

        usecase = spec['usecase']

        name = request.GET.get('name', None)
        if name is None:
            logger.exception("Missing name of the result")
            return HttpResponseRedirect(reverse(r.namespace + ":result_index"))

        data = request.GET.get('data', '{}')
        try:
            data = json.loads(data)
        except:
            logger.exception("Missing data dictionary required for workflows")
            return HttpResponseRedirect(reverse(r.namespace + ":result_index"))

        template = self.get_template(spec, 'workflow_index')

        targets = AppActionTarget.objects.filter(nature__in=self.get_supported_actions(request, spec, policy))

        return render(request,
                      template,
                      {
                          'app': self,
                          'spec': spec,
                          'usecase': usecase,
                          'basenamespace': r.namespace,
                          "name": name,
                          'data': data,
                          'targets': targets
                      })

    ################################################################
    # API
    ################################################################
    @log_activity("app_policy_index_api", nature="application")
    def api_policy_index(self, request, instancename):
        """
        Return the queryset
        """
        from dashboard.apiv2 import lookup_specification

        spec = lookup_specification(name=instancename,
                                    category=self.category)
        if spec is None:
            return {
                "status": "failure",
                "message": f"Unknown specification: {self.name}"
            }

        namespace = spec.get('namespace', 'default')
        PolicyModel    = self.get_model(spec, 'app_policy')

        qs = PolicyModel.objects.filter(active=True,
                                        appname=self.name,
                                        namespace=namespace)
        policies = [p.export(spec) for p in qs]

        return {
            "status": "success",
            "data": policies
        }


    ################################################################
    # Ninja Routing/URLS setup
    ################################################################
    def get_router(self):

        from ninja import Router, Query, Schema

        router = Router()

        @router.get("/app/" + self.name + "/{appname}/policies",
                    url_name=self.name+"_policy_index",
                    summary="List policies defined in this app",
                    tags=[self.name])
        def api_policies_index(request, appname):
            """
            List policies
            """
            return self.api_policy_index(request, instancename=appname)

        return router
