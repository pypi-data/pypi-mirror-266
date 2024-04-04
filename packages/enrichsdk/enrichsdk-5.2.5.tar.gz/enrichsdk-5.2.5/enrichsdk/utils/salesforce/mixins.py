import os
import sys
import json
import requests
import logging
import time
import csv
import re
import traceback

from django.urls import reverse, resolve
from django.conf.urls import url, include
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.utils.timezone import localtime

from dateutil import parser as dateparser

from enrichsdk.app.utils import clean_and_validate_widgets
from enrichsdk.lib import get_credentials_by_name

logger = logging.getLogger("app")

class SalesforceClient:

    def __init__(self, cred):

        if isinstance(cred, str):
            self.cred = get_credentials_by_name(cred)
        else:
            self.cred = cred
        self.baseurl = self.cred['url']
        self.token = None
        self.salesforce_version = "v58.0"

    def get_token(self, force=False):
        """
        Get access token...
        """
        sample_token = {
            'access_token': '00D7j000000H9Ht!AR...',
            'instance_url': 'https://acmecompanycompany--preprod.sandbox.my.salesforce.com',
            'id': 'https://test.salesforce.com/id/00D7j000000H9HtEAK/0057j0000053bRfAAI',
            'token_type': 'Bearer',
            'issued_at': '1697972695996',
            'signature': 'BQ+dEwXSrqZcZtqXYGSYR2B+9+3eftIeBjT92Dv2YYI='
        }

        # Assumption. We dont know when the token will expire. It is
        # said to be 2 hours in documentation
        timeout = 3600*1000
        now = int(1000*time.time())
        if ((not force) and
            (self.token is not None) and
            (isinstance(self.token, dict)) and
            ('access_token' in self.token) and
            (now < (int(self.token['issued_at']) + timeout))):
            return self.token['access_token']

        tokenurl = self.baseurl + "/services/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Construct the oauth request
        cred = self.cred
        data = {
            "grant_type": "password",
            "client_id": cred['client_id'],
            "client_secret": cred['client_secret'],
            "username": cred['username'],
            "password": cred['password'] + cred['client_security_token']
        }

        msg = ""
        msg += f"Token URL: {tokenurl}\n"
        for k, v in data.items():
            if k != "password":
                msg += f"{k}: {str(v)[:8]}...\n"
            else:
                msg += f"{k}: ****...\n"
            result = requests.post(tokenurl, data=data, headers=headers)
        try:
            self.token = result.json()
            if result.status_code == 200:
                logger.debug("Salesforce token obtained",
                             extra={
                                 'data': msg
                             })
            else:
                logger.error("Failed to obtained Salesforce token",
                             extra={
                             'data': msg + str(result.content)
                             })
        except:
                logger.exception("Failed to obtained Salesforce token",
                             extra={
                             'data': msg + str(result.content)
                             })

        return self.token['access_token']

    def access_salesforce(self, url, method="get",
                          params={}, data={},
                          request=None):

        token = self.get_token()
        url = self.baseurl + url
        headers = {
            'Authorization': f"Bearer {token}"
        }

        if method == "get":
            result = requests.get(url, params=params, headers=headers)
        elif method == "post":
            result = requests.post(url, params=params, headers=headers, json=data)
        elif method == "patch":
            result = requests.patch(url, params=params, headers=headers, json=data)
        else:
            raise Exception(f"Unknown access method: {method}")

        if result.status_code >= 400:
            logger.error("Failed to access Salesforce",
                         extra={

                             'data': f"URL: {url}\nOutput: {result.content}"
                         })
        try:
            if method != "patch":
                status, result = result.status_code, result.json()
            else:
                status, result = result.status_code, {}

            # [{"message":"Jurisdiction: bad value for restricted picklist field: State of Washington","errorCode":"INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST","fields":["Jurisdiction__c"]}]
            if ((request is not None) and
                (isinstance(result, (dict, list))) and
                (len(result) > 0)):
                res = result
                if isinstance(res, list):
                    res = res[0]
                if isinstance(res, dict) and ("message" in res):
                    messages.error(request, "Salesforce message: " + res['message'])

            if 'nextRecordsUrl' in result:
                messages.error(request, "Internal error. A few search results were not processed. Please contact support")

            return status, result
        except:
            logger.exception("Failed to access Salesforce",
                             extra={
                                 'data': f"URL: {url}\n"
                             })

        raise Exception("Failed to access Salesforce")

    def run_query(self, query, request=None):

        query = re.split(r"\s+", query)
        query = "+".join(query)
        opurl = f"/services/data/{self.salesforce_version}/query/?q={query}"

        status, result = self.access_salesforce(opurl, request=request)
        if status >= 400:
            raise Exception("Failed to run query")
        return result

    def get_opportunity_by_id(self, oppid, request=None):

        opurl = f"/services/data/{self.salesforce_version}/sobjects/Opportunity/{oppid}"
        status, result = self.access_salesforce(opurl, request=request)
        if status >= 400:
            raise Exception("Failed to get opportunity")
        return result

    def describe_opportunity(self, request=None):

        opurl = f"/services/data/{self.salesforce_version}/sobjects/Opportunity/describe"
        status, result = self.access_salesforce(opurl, request=request)
        if status >= 400:
            raise Exception("Failed to describe opportunity")
        return result

    def get_opportunities(self, limit=200, columns=None, request=None):

        fields = "FIELDS(ALL)"
        if columns is not None:
            fields = ",".join(columns)

        opurl = f"/services/data/{self.salesforce_version}/query/?q=SELECT+{fields}+FROM+Opportunity+ORDER+BY+LastModifiedDate+DESC+LIMIT+{limit}"

        status, result = self.access_salesforce(opurl, request=request)
        if status >= 400:
            raise Exception("Failed to query for opportunities")
        return result

    def get_opportunity_detail(self, oppid, request=None):

        opurl = f"/services/data/{self.salesforce_version}/sobjects/Opportunity/{oppid}"

        status, result = self.access_salesforce(opurl, request=request)
        if status >= 400:
            raise Exception("Failed to get opportunity detail")
        return result

    def add_opportunity(self, data, request=None):
        opurl = f"/services/data/{self.salesforce_version}/sobjects/Opportunity"
        status, result = self.access_salesforce(opurl, method="post", data=data, request=request)
        if status >= 400:
            raise Exception("Failed to add opportunity")
        return result

    def update_opportunity(self, oppid, data, request=None):
        opurl = f"/services/data/{self.salesforce_version}/sobjects/Opportunity/{oppid}"
        status, result = self.access_salesforce(opurl,
                                                method="patch",
                                                data=data,
                                                request=request)
        if status >= 400:
            raise Exception("Failed to add opportunity")
        return result

    def get_accounts(self, limit=200, columns=None, request=None):

        fields = "FIELDS(ALL)"
        if columns is not None:
            fields = ",".join(columns)

        opurl = f"/services/data/{self.salesforce_version}/query/?q=SELECT+{fields}+FROM+Account+ORDER+BY+LastModifiedDate+DESC+LIMIT+{limit}"

        status, result = self.access_salesforce(opurl, request=request)
        if status >= 400:
            raise Exception("Failed to query for opportunities")
        return result

    def add_account(self, data, request=None):
        opurl = f"/services/data/{self.salesforce_version}/sobjects/Account"
        status, result = self.access_salesforce(opurl,
                                                method="post",
                                                data=data, request=request)
        if status >= 400:
            raise Exception("Failed to add account")
        return result

    def get_account_by_id(self, accid, request=None):

        opurl = f"/services/data/{self.salesforce_version}/sobjects/Account/{accid}"
        status, result = self.access_salesforce(opurl, request=request)
        if status >= 400:
            raise Exception(f"Failed to get account details: {accid}")
        return result

#############################################
#=> Fields in Salesforce Opportunity Object
#############################################
# Account_Name__c: null,
# Account_Region__c: null,
# Active_Headcount__c: null,
# Amount: 4810308.0,
# Amount_Lost__c: 0.0,
# Amount_M__c: 5.0,
# LastActivityDate: null,
# LastAmountChangedHistoryId: null,
# LastCloseDateChangedHistoryId: null,
# LastModifiedById: 0057j0000053bRfAAI,
# LastModifiedDate: 2023-10-19T17:37:53.000+0000,
# ....

class SalesforceBaseMixin:

    def salesforce_update_urlpatterns(self, prefix, urlpatterns):
        urlpatterns.extend([
            url(f'^{prefix}[/]?$', self.salesforce_index, name="salesforce_index"),
            url(f'^{prefix}/detail/(?P<oppid>[a-zA-Z0-9]+)[/]?$', self.salesforce_detail, name="salesforce_detail"),
        ])

    def salesforce_update_templates(self, templates):
        templates.update({
            'salesforce_index': 'sharedapp/generic_index.html',
            'salesforce_detail': 'sharedapp/generic_index.html',
        })

    def salesforce_get_server_name(self, request, spec):
        return spec.get('database', 'salesforce').title()

    ######################################################
    # Matching
    ######################################################
    def get_client(self, request, spec):

        # Get the salesforce client...
        cred = spec['cred']
        cred = get_credentials_by_name(cred)
        if hasattr(self, "salesforce_client"):
            client = self.salesforce_client
        else:
            client = self.salesforce_client = SalesforceClient(cred)

        return cred, client

    def find_overlap_str(self, new, existing):

        if not isinstance(existing, str) or len(existing) == 0:
            return 0

        skip = ['pension', 'plan', 'inc', 'retirement']

        new = re.split(r"[\s\.,]+", new.lower().strip())
        new = [n for n in new if len(n) >= 3 and (n not in skip)]
        if len(new) == 0:
            return 0

        existing = re.split(r"[\s\.,]+", existing.lower().strip())
        existing = [n for n in existing if len(n) >= 3 and (n not in skip)]
        if len(existing) == 0:
            return 0

        overlap = len([x for x in new if x in existing])/len(existing)

        return overlap

    def find_overlap_name(self, new, existing):
        overlap = self.find_overlap_str(new, existing)
        overlap = int(overlap * 100)
        return overlap

    def find_overlap_date(self, dt1, dt2, days=30):

        try:
            if not isinstance(dt1, (date, datetime)):
                dt1 = dateparser.parse(dt1)
        except:
            return 0

        try:
            if not isinstance(dt2, (date, datetime)):
                dt2 = dateparser.parse(dt2)
        except:
            return 0

        diff = dt2-dt1
        return 1 if abs(diff.days) < days else 0

    def find_overlap_numeric(self, amt1, amt2, threshold=2):

        if ((amt1 is None) or
            (pd.isnull(amt1)) or
            (amt2 is None) or
            (pd.isnull(amt2)) or
            (not isinstance(amt1, (int, float))) or
            (not isinstance(amt2, (int, float))) or
            (amt1 <= 0) or
            (amt2 <= 0)):
            return 0

        ratio = (amt1/amt2) if amt1 > amt2 else (amt2/amt1)
        return 1 if ratio < threshold else 0

    def find_overlap_combined(self, modelvars, opportunity):

        total_overlap = 0

        for col in ['Plan Name', 'State']:
            overlap = self.find_overlap_name(modelvars[col], opportunity[col])
            total_overlap += 1

        return int((100*total_overlap/4))


    #################################################################
    # All Salesforce
    #################################################################
    def salesforce_index_get_extra_header_components(self, request, spec):

        r = resolve(request.path)
        return []

    def salesforce_index_finalize_entry(self, request, spec, opportunity, entry):
        return entry

    def salesforce_index_finalize_widgets(self, request, spec,
                                          opportunities, widgets):
        return widgets

    def salesforce_index_get_extra_actions(self, request, spec,
                                           opportunity,
                                           entry):
        return {}, []

    def salesforce_index_get_opportunities(self, request, spec):

        cred, client = self.get_client(request, spec)

        opportunities = client.get_opportunities(columns=[
            "Name",
            "Amount",
            "Id",
            "CreatedDate"
        ], request=request)

        return opportunities

    def salesforce_index_get_columns(self, request, spec, data):

        columns = [
            "Added", 'Name', "Amount (M$)",
        ]

        workflowcols = []
        detailcols = []

        if len(data) > 0:
            for k in data[0].keys():
                if k in columns:
                    continue
                if k.startswith("ACTION_"):
                    detailcols.append(k)
                else:
                    workflowcols.append(k)
        columns += [
            ('Workflow', workflowcols),
            ('Details', detailcols)
        ]
        return columns

    def salesforce_index_finalize_data(self, request, spec, data):
        return data

    def salesforce_index(self, request, spec):

        r = resolve(request.path)

        usecase = spec['usecase']
        namespace = spec['namespace']
        cred = spec['cred']
        if isinstance(cred, str):
            cred = get_credentials_by_name(spec['cred'])

        # First get the opportunities
        opportunities = self.salesforce_index_get_opportunities(request, spec)

        workflowcols = []
        data = []
        for o in opportunities.get('records',[]):

            amount = o['Amount']
            if amount is None:
                amount = 0
            amount = round(amount/10**6, 1)

            dt = dateparser.parse(o['CreatedDate'])
            detailurl = reverse(r.namespace + ":salesforce_detail",
                                kwargs={
                                    'oppid': o['Id']
                                })
            entry = {
                "Added": dt.replace(microsecond=0).strftime("%Y-%m-%d"),
                "Amount (M$)": amount,
                "Name": f'<a href="{detailurl}">{o["Name"]}</a>',
                "ACTION_SALESFORCE": {
                    "title": "Details",
                    "alt": "",
                    "class": "",
                    "template": "action_icon_compact",
                    "target": "_blank",
                    "icon": "salesforce_24x24",
                    "url": f"{cred['url']}/{o['Id']}"
                },
                "ACTION_DYNAMICS": {
                    "title": "Details",
                    "alt": "",
                    "class": "",
                    "template": "action_icon_compact",
                    "target": "_blank",
                    "icon": "dynamics_24x24",
                    "url": f"{cred['url']}/{o['Id']}"
                },
            }

            # Any cleanup before adding extra actions...
            entry = self.salesforce_index_finalize_entry(request, spec, o, entry)

            # Now add actions...
            extra, order = self.salesforce_index_get_extra_actions(request, spec, o, entry)
            entry.update(extra)

            data.append(entry)


        # How should I structure the output columns
        columns = self.salesforce_index_get_columns(request, spec, data)

        # Any header actions..
        extra_header_components = self.salesforce_index_get_extra_header_components(request, spec)

        server = self.salesforce_get_server_name(request, spec)
        widget = {
            "name": f"Opportunities in {server}",
            "description": f"Recent entries and not the complete list",
            "type": "full_width_table_compact_actions",
            "columns": columns,
            "search": True,
            "rows": data,
            "order": [[0, "desc"]],
            "td_class": "white-space-normal wordwrap",
            "thead_th_class": "",
            "header_components": {
                "components": [
                    {
                        "template": "action_search"
                    }
                ]
            }
        }

        widgets = [widget]

        # Do any extra cleanup
        widgets = self.salesforce_index_finalize_widgets(request, spec,
                                                         opportunities,
                                                         widgets)

        clean_and_validate_widgets(widgets)

        server = self.salesforce_get_server_name(request, spec)
        data = {
            "title": server,
            "sidebar_targets": self.get_sidebar(request, spec),
            "breadcrumb": server,
            "widgets": widgets
        }

        # Cleanup and add any final note..
        data = self.salesforce_index_finalize_data(request, spec, data)

        template = self.get_template(spec, 'salesforce_index')
        return render(request,
                      template,
                      {
                          'app': self,
                          'usecase': usecase,
                          'spec': spec,
                          'basenamespace': r.namespace,
                          'data': data
                      })

    def salesforce_detail_get_opportunity(self, request, spec, oppid):

        cred, client = self.get_client(request, spec)

        return client.get_opportunity_by_id(oppid, request=request)

    def salesforce_detail(self, request, spec, oppid):

        r = resolve(request.path)
        server = self.salesforce_get_server_name(request, spec)

        usecase = spec['usecase']
        namespace = spec['namespace']

        sfindexurl = reverse(r.namespace + ":salesforce_index")

        widgetspecs = []

        # => Get the opportunity object...
        try:
            detail = self.salesforce_detail_get_opportunity(request, spec, oppid)
        except:
            traceback.print_exc()
            logger.exception(f"Invalid opportunity: {oppid}")
            messages.error(request, f"Invalid opportunity: {oppid}")
            return HttpResponseRedirect(sfindexurl)

        accounts = {}
        data = []
        for name, value in detail.items():
            if not isinstance(value, str):
                value = str(value)
            data.append({
                "Attribute": name,
                "Value": value
            })

        name = detail['Name']
        widgetspecs.append({
            "name": name,
            "description": f"Opportunity detail in {server}",
            "data": data
        })

        columns = [
            "Attribute", "Value"
        ]

        widgets = []
        for widgetspec in widgetspecs:
            widget = {
                "name": widgetspec['name'],
                "description": widgetspec['description'],
                "type": "full_width_table_compact_actions",
                "columns": columns,
                "search": True,
                "rows": widgetspec['data'],
                "order": [[0, "asc"]],
                "td_class": "white-space-normal wordwrap",
                "thead_th_class": "",
                "header_components": {
                    "components": [
                        {
                            "template": "action_search"
                        }
                    ]
                }
            }
            widgets.append(widget)

        clean_and_validate_widgets(widgets)

        server = self.salesforce_get_server_name(request, spec)
        data = {
            "title": server,
            "sidebar_targets": self.get_sidebar(request, spec),
            "breadcrumbs": [
                {
                    "name": server,
                    "url": reverse(r.namespace + ":salesforce_index"),
                },
                {
                    "name": "Detail"
                }
            ],
            "widgets": widgets
        }

        template = self.get_template(spec, 'salesforce_detail')
        return render(request,
                      template,
                      {
                          'app': self,
                          'usecase': usecase,
                          'spec': spec,
                          'basenamespace': r.namespace,
                          'data': data
                      })


class SalesforceDatasetMixin:
    """
    Code had handles the integration between salesforce and Dataset
    """
    def salesforce_dataset_update_urlpatterns(self, prefix, urlpatterns):

        urlpatterns.extend([
            url(f'^{prefix}/post/(?P<datasetpk>[0-9a-zA-Z-_ .]+)/action[/]?$', self.salesforce_dataset_action, name="salesforce_dataset_action"),
            url(f'^{prefix}/post/(?P<datasetpk>[0-9a-zA-Z-_ .]+)/select[/]?$', self.salesforce_dataset_select, name="salesforce_dataset_select"),
            url(f'^{prefix}/post/(?P<datasetpk>[0-9a-zA-Z-_ .]+)/verify[/]?$', self.salesforce_dataset_verify, name="salesforce_dataset_verify"),
        ])

    def salesforce_dataset_update_templates(self, templates):
        templates.update({
            'salesforce_dataset_action': 'sharedapp/generic_index.html',
            'salesforce_dataset_verify': 'sharedapp/generic_index.html',
            'salesforce_dataset_select': 'sharedapp/generic_index.html'
        })

    def salesforce_dataset_select(self, request, spec, datasetpk):
        """
        Select whether to create or update
        """

        testmode = spec.get('testmode', False)
        server = self.salesforce_get_server_name(request, spec)

        usecase = spec['usecase']
        namespace = spec['namespace']
        r = resolve(request.path)

        cred, client = self.get_client(request, spec)

        dataseturl = reverse(r.namespace + ":dataset_index")
        validateurl = reverse(r.namespace + ":dataset_validate",
                              kwargs={
                                  'pk': datasetpk
                              })
        verifyurl = reverse(r.namespace + ":salesforce_dataset_verify",
                        kwargs={
                                'datasetpk': datasetpk
                        })
        redirect = HttpResponseRedirect(validateurl)

        # => Get models
        LLMDatasetModel = self.get_model(spec, 'llmdataset')

        # Get the dataset
        try:
            dataset = LLMDatasetModel.objects.get(pk=datasetpk)
        except LLMDatasetModel.DoesNotExist:
            messages.error(request, 'Invalid dataset')
            return HttpResponseRedirect(reverse(r.namespace + ":dataset_index"))

        ##########################################################
        # => First get all the model parameters
        ##########################################################
        try:
            modelvars = dataset.values.get('modelvar', [])
            if len(modelvars) == 0:
                messages.error(request, "Not posted. Please save first")
                return redirect

            # Convery into a dictionary
            modelvars = { v['name'] : v['value'] for v in modelvars}

        except:
            logger.exception("Unable to post to salesforce")
            messages.error(request, f'Internal error. Unable to post to {server}')
            return redirect

        ##########################################################
        #=> Extract Some basic information...
        ##########################################################
        plan_name = modelvars['Plan Name']
        plan_sponsor = modelvars['Plan Sponsor']
        consultant = modelvars['Consultant']
        estimated_size = modelvars['Estimated Size']
        state = modelvars['State']

        ##########################################################
        #=> Now search last N opportunities
        ##########################################################
        opportunities = client.get_opportunities(columns=[
            "Name",
            "Plan Name",
            "Plan Sponsor",
            "CreatedDate",
            "Due Date",
            "Estimated Size",
            "Deal Type",
            "Amount",
            "Stage",
            "Consultant",
            "Id"
        ], request=request)
        data = []
        for o in opportunities.get('records',[]):

            name = o["Plan Name"]

            # Keep only test. For dev/testing...
            if testmode:
                 if ((name is None) or ("ABC" not in name)):
                     continue

            dt = dateparser.parse(o['CreatedDate'])
            amount = o['Amount']
            if amount is None:
                amount = 0
            if amount > 100000:
                amount = round(amount/10**6, 1)

            detailurl = reverse(r.namespace + ":salesforce_detail",
                                kwargs={
                                    'oppid': o['Id']
                                })

            overlap = self.find_overlap_combined(modelvars, o)

            data.append({
                "Conflict Score": overlap,
                "Added": localtime(dt.replace(microsecond=0)),
                "Name": f'<a href="{detailurl}">{o["Name"]}</a>',
                "Plan Sponsor": o['Plan Sponsor'],
                "Consultant": o['Consultant'],
                "Deal Type": o["Deal Type"],
                "State": o["State"],
                "Amount (M$)": amount,
                "ACTION_EDIT": {
                    "title": "Edit This Opportunity",
                    "alt": "",
                    "class": "btn",
                    "template": "action_icon_compact",
                    "icon": "edit_24dp_1",
                    "text": "Update",
                    "url": verifyurl + f"?action=edit&opportunityid={o['Id']}"
                },
            })

        columns = [
            "Conflict Score", "Added", 'Name', "Plan Sponsor",
            "Consultant","Deal Type", "State",
            "Amount (M$)",
            ("Action", ["ACTION_EDIT"])
        ]

        widget = {
            "name": f"Update Existing Opportunity: {plan_name}",
            "description": "Select opportunity to edit. Note that this shows ONLY the most recent 75 opportunities. Make sure you look for placeholder opportunities as well.",
            "type": "full_width_table_compact_actions",
            "columns": columns,
            "search": True,
            "rows": data,
            "order": [[0, "desc"], [1, "desc"]],
            "td_class": "white-space-normal wordwrap",
            "thead_th_class": "",
            "header_components": {
                "components": [
                    {
                        "template": "action_search"
                    }
                ]
            }
        }

        widgets = [widget]

        #=> Add notes..
        widget = {
            "name": f"Create Opportunity: {plan_name}",
            "description": "Notes on the post",
            "type": "full_width_form",
            "submit": "Create",
            "action": verifyurl,
            "hidden_vars": {
                "action": "create"
            },
            "text": f"""\
<ol>
<li>Plan Name: {plan_name}</li>
<li>Plan Sponsor: {plan_sponsor}</li>
<li>Consultant: {consultant}</li>
<li>State: {state}</li>
<li>Estimated Size: {estimated_size}</li>
</ol>
<p>Note that state, estimated size and other variables will be cleaned to make sure it is consistent with database format. Make sure you check the "New Value" column for all variables</p>
""",
            "td_class": "white-space-normal wordwrap",
            "header_components": {
                "components": [
                    {
                        "template": "action_icon_compact",
                        "icon": "add_circle_outline_24dp_1",
                        "url": verifyurl + f"?action=create",
                        "title": "Create new opportunity",
                    },
                ]
            }
        }
        widgets.insert(0, widget)

        widget = {
            "name": "RFP Workflow",
            "type": "workflow",
            "order": [
                {
                    "name": "Upload RFP",
                    "url": dataseturl
                },
                {
                    "name": "Validate Parameters",
                    "url": validateurl
                },
                f"Prepare Post to {server}",
                f"Approve Post to {server}",
            ],
            "currpos": 2,
            "class": "mb-2"
        }
        widgets.insert(0, widget)

        clean_and_validate_widgets(widgets)

        data = {
            "title": f"Update or Create Opportunity: {dataset.name}",
            "sidebar_targets": self.get_sidebar(request, spec),
            "breadcrumbs": [
                {
                    "name": "Datasets",
                    "url": reverse(r.namespace + ":dataset_index")
                },
                {
                    "name": "Validate",
                    "url": validateurl
                },
                {
                    "name": f"Approve {server} Post"
                }
            ],
            "widgets": widgets
        }

        template = self.get_template(spec, 'salesforce_dataset_select')
        return render(request,
                      template,
                      {
                          'app': self,
                          'usecase': usecase,
                          'spec': spec,
                          'basenamespace': r.namespace,
                          'data': data,
                      })

    def field_specific_cleanup(self, field, value):

        # Floating point number
        if field in ['Estimated Size']:
            matches = re.findall(r"(\d+\.\d+|\d+)]?", value.replace(",",""))

            if matches is None:
                value = None
            else:
                value = float(matches[0])
                if value > 10**6:
                    # exact number is mentioned.
                    value = round(value/10**6, 2)

        if field in [
                "Final Quote",
                "Request for Quotation",
                "Intent Due",
                "Prelim Quotes Due",
                "Final Quote",
                "Premium Transfer Due",
                "Liability Assumption Date",
                "First Payment (Financial)"
        ]:
            try:
                value = dateparser.parse(value).date().isoformat()
            except:
                # traceback.print_exc()
                value = None

        return value

    def salesforce_dataset_verify(self, request, spec, datasetpk):
        """
        Post to salesforce
        """

        server = self.salesforce_get_server_name(request, spec)
        usecase = spec['usecase']
        namespace = spec['namespace']
        r = resolve(request.path)

        action = request.GET.get('action', None)
        action_oppid = request.GET.get('opportunityid', None)
        action_oppid = None if str(action_oppid).lower() == "none" else action_oppid

        dataseturl = reverse(r.namespace + ":dataset_index")
        validateurl = reverse(r.namespace + ":dataset_validate",
                              kwargs={
                                  'pk': datasetpk
                              })
        redirect = HttpResponseRedirect(validateurl)
        selecturl = reverse(r.namespace + ":salesforce_dataset_select",
                              kwargs={
                                  'datasetpk': datasetpk
                              })
        selectredirect = HttpResponseRedirect(selecturl)

        # => Is this an edit or create...
        if action not in ['create', 'edit']:
            messages.error(request, f"Invalid {server} action. Should be create or edit. Not {action}")
            return selectredirect

        if ((action == "edit") and
            ((not isinstance(action_oppid, str)) or
             (len(action_oppid) <= 16))):
            messages.error(request, f"Invalid {server} opportunity ID. Should have atleast 16 characters {len(action_oppid)}")
            return selectredirect

        cred, client = self.get_client(request, spec)

        # => Get models
        LLMDatasetModel = self.get_model(spec, 'llmdataset')

        # Get the dataset
        try:
            dataset = LLMDatasetModel.objects.get(pk=datasetpk)
        except LLMDatasetModel.DoesNotExist:
            messages.error(request, 'Invalid dataset')
            return HttpResponseRedirect(reverse(r.namespace + ":dataset_index"))

        ##########################################################
        # => First get all the model parameters
        ##########################################################
        try:
            modelvars = dataset.values.get('modelvar', [])
            if len(modelvars) == 0:
                messages.error(request, "Not posted. Please save first")
                return redirect

            # Convery into a dictionary
            varposition = { v['name'] : f"{idx:02d}" for idx, v in enumerate(modelvars)}
            modelvars = { v['name'] : v['value'] for v in modelvars}

        except:
            logger.exception("Unable to post to salesforce")
            messages.error(request, f'Internal error. Unable to post to {server}')
            return redirect

        ##########################################################
        #=> Some basic information...
        ##########################################################
        plan_name = modelvars['Plan Name']
        plan_sponsor = modelvars['Plan Sponsor']
        consultant = modelvars['Consultant']

        ##########################################################
        # => Existing opportunity
        ##########################################################
        opportunity = {}
        if action == "edit":
            try:
                opportunity = client.get_opportunity_by_id(action_oppid, request=request)
            except:
                messages.error(request, f"Invalid opportunity ID: {action_oppid}")
                logger.exception(f"Invalid opportunity ID: {action_oppid}")
                return selectredirect

        ##########################################################
        # => Now construct the widgets...
        ##########################################################
        def detect_change(e):
            existing = e['Existing Value']
            new = e['New Value']
            if (((existing in [None, '', "None"]) and (new in [None, '', "None"])) or
                (existing == new)):
                return "<i class='fa fa-check' style='color: green'></i> YES"
            return "<i class='fa fa-exclamation-triangle' style='color: red'></i> NO"

        mapped = []
        error_fields = []
        # => Now add the rest of the entries...
        for k, v in modelvars.items():

            v1 = self.field_specific_cleanup(k, v)
            entry = {
                "RFP Param No": varposition.get(k, "50"),
                "RFP Parameter": k,
                "RFP Value": v,
                f"{server} Field Desc": k,
                f"{server} Field Name": k,
                "New Value": v1,
                "Existing Value": opportunity.get(k, ""),
            }

            # Add a check for all fields...
            entry["Match"] = detect_change(entry)
            entry['Post'] = ''
            if (("YES" not in entry['Match']) and
                (entry['New Value'] is not None)):
                entry["Post"] =  f"""\
<input class="form-check-input checkboxinput" type="checkbox" name="post" data-varname="{entry["RFP Parameter"]}" checked=""/>
                """
            mapped.append(entry)

        columns = [
            "RFP Param No", "RFP Parameter", "RFP Value",
            f"{server} Field Desc", f"{server} Field Name"
        ]

        ordercol = 0
        if action == "edit":
            columns.extend(["Existing Value", "New Value", "Match", "Post"])
            # ordercol = 6
        else:
            columns.extend(["New Value"])

        widgets = []
        for name, description, data in [
                ("Mapped", f"Posted to {server}", mapped),
        ]:
            if len(data) == 0:
                continue

            widget = {
                "name": f"{name} Parameters: {plan_name}",
                "description": description,
                "type": "full_width_table_compact_actions",
                "columns": columns,
                "search": True,
                "rows": data,
                "page_size": 50,
                "order": [[ordercol, "asc"]],
                "td_class": "white-space-normal wordwrap",
                "thead_th_class": "",
                "header_components": {
                    "components": [
                        {
                            "template": "action_search"
                        }
                    ]
                }
            }

            widgets.append(widget)

        #=> Add notes..
        notes ="""<ol>\n"""
        if action == "edit":
            notes += f"<li><strong>NOTE: You are UPDATING an existing Opportunity ({opportunity['Name']})</strong></li>"
        else:
            notes += f"<li><strong>NOTE: You are creating/adding a new Opportunity </strong></li>"
        notes += f"""\
<li>Please review existing opportunity, intermediary, and sponsor lists</li>
<li>Some fields require default values such as Closing Date</li>
<li>Note that state, estimated size and other variables will be cleaned to make sure it is consistent with {server} format. Make sure you check the "New Value" column for all variables</li>
"""
        notes += """</ol>"""

        widget = {
            "name": f"Instructions & Notes: {plan_name}",
            "description": "Notes on the post",
            "type": "full_width_text",
            "text": notes,
            "td_class": "white-space-normal wordwrap",
        }
        widgets.insert(0, widget)

        widget = {
            "name": "RFP Workflow",
            "type": "workflow",
            "order": [
                {
                    "name": "Upload RFP",
                    "url": dataseturl
                },
                {
                    "name": "Validate Parameters",
                    "url": validateurl
                },
                {
                    "name": f"Prepare Post to {server}",
                    "url": selecturl,
                },
                f"Approve Post to {server}"
            ],
            "currpos": 3,
            "class": "mb-2"
        }
        widgets.insert(0, widget)

        widget = {
            "name": f"Post to {server}: {plan_name}",
            "description": "Take action on the above content",
            "type": "full_width_form",
            "text": """
<ol>
<li>Check everything</li>
</ol>
            """,
            "hidden_vars": {
                "action": action,
                "opportunityid": action_oppid,
                "checkedvars": ""
            },
            "elements": [
                {
                    "type": "select",
                    "name": "stagename",
                    "id": "stagename",
                    "label": "StageName",
                    "choices": [
                        "Bid",
                        "Onboarding",
                        "Ongoing"
                    ],
                    "selected_choice": "Bid"
                },
                {
                    "type": "textarea",
                    "name": "comments",
                    "id": "comments",
                    "rows": 5,
                    "cols": 120,
                    "placeholder": "Please enter any comments here. They will be saved in the comments field",
                    "value": "",
                    "label": f"Comments",
                },

            ],
            "action": reverse(r.namespace + ":salesforce_dataset_action",
                              kwargs={
                                  'datasetpk': datasetpk
                              }),
            "submit": "Yes",
            "submit_class": "confirmbtn",
            "submit_header": f"Confirm Post to {server}",
            "submit_body": f"By clicking Yes, you are confirming the accuracy of the data. Once you click, the data will be sent to {server}. In case of an update, any prior data will be overwritten in a non reversible manner and for a new record, a duplicate may be created. Please verify on/in {server}.",
            "submit_handler": """
// Extract the checked boxes and post them...
var varlist = new Array();
$('input[type=checkbox]').each(function () {
   if ($(this).prop('checked')) {
       var varname = $(this).data('varname');
       if (typeof varname != 'undefined'){
         varlist.push(varname)
       }
   }
});
$('input[name="checkedvars"]').val(JSON.stringify(varlist));
            """,

            "td_class": "white-space-normal wordwrap",
        }

        widgets.append(widget)


        clean_and_validate_widgets(widgets)

        data = {
            "title": f"Approve Post to {server}: {dataset.name}",
            "sidebar_targets": self.get_sidebar(request, spec),
            "breadcrumbs": [
                {
                    "name": "Datasets",
                    "url": reverse(r.namespace + ":dataset_index")
                },
                {
                    "name": "Validate",
                    "url": validateurl
                },
                {
                    "name": f"Approve {server} Post"
                }
            ],
            "widgets": widgets
        }

        # Make note of any errors you may have seen
        if len(error_fields) > 0:
            messages.warning(request, f"Please double check the following fields: {','.join(error_fields)}")

        template = self.get_template(spec, 'salesforce_dataset_verify')
        return render(request,
                      template,
                      {
                          'app': self,
                          'usecase': usecase,
                          'spec': spec,
                          'basenamespace': r.namespace,
                          'data': data,
                      })

    def salesforce_dataset_action(self, request, spec, datasetpk):
        """
        Post to salesforce
        """

        server = self.salesforce_get_server_name(request, spec)

        action = request.GET.get('action', None)
        action_oppid = request.GET.get('opportunityid', None)
        action_oppid = None if str(action_oppid).lower() == "none" else action_oppid

        # => Get models
        LLMDatasetModel = self.get_model(spec, 'llmdataset')

        # Get the dataset
        try:
            dataset = LLMDatasetModel.objects.get(pk=datasetpk)
        except LLMDatasetModel.DoesNotExist:
            messages.error(request, 'Invalid dataset')
            return HttpResponseRedirect(reverse(r.namespace + ":salesforce_detail",
                                                kwargs={
                                                    "oppid": action_oppid
                                                }))
        dataset_name = dataset.name

        usecase = spec['usecase']
        namespace = spec['namespace']
        r = resolve(request.path)

        # Create an audit record
        if hasattr(self, 'audit_add'):
            self.audit_add(request, spec,
                           action=f"salesforce_{action}",
                           summary=f"Post to {server}",
                           details={
                               'dataset_pk': datasetpk,
                               'dataset_name': dataset_name,
                               'opportunity_id': action_oppid,
                           })

        # What should be redirect to...
        if action == "create":
            messages.info(request, "Created dummy opportunity")
            return HttpResponseRedirect(reverse(r.namespace + ":salesforce_index"))
        else:
            messages.info(request, "Updated dummy opportunity")
            return HttpResponseRedirect(reverse(r.namespace + ":salesforce_detail",
                                                kwargs={
                                                    "oppid": action_oppid
                                                }))

if __name__ == "__main__":

    salesforce = SalesforceClient(cred="acme-salesforce")

    results = salesforce.get_opportunities()
    print(json.dumps(results, indent=4))

    #results = salesforce.describe_opportunity()
    #print(json.dumps(results, indent=4))

