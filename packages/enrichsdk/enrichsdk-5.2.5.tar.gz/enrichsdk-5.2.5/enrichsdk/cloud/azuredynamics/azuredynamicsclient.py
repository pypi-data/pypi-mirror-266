import os
import re
import requests
import logging
from urllib.parse import urlencode, unquote_plus

logger = logging.getLogger("app")

__all__ = ['AzureDynamicsClient']

#
# AzureDynamicsClient to invoke Dynamics365 web apis.
#
class AzureDynamicsClient:
    api_path = "api/data/v9.2"

    def __init__(self, domain, tenant_id, client_id, client_secret, login_url, grant_type, access_token=None):
        self.domain = domain.strip("/")
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.login_url = login_url
        self.grant_type = grant_type

        self.headers = {
            "Accept": "application/json, */*",
            "content-type": "application/json; charset=utf-8",
        }
        if access_token is not None:
            self.set_access_token(access_token)

    #
    # Sets the access token for use in this library in the header information to make request calls.
    # This is  obtained after successful login.
    #
    def set_access_token(self, token):
        assert token is not None, "The token cannot be None."
        self.access_token = token
        self.headers["Authorization"] = "Bearer " + self.access_token

    #
    # Does the login to get the access token and sets it for use in the library.
    #
    def do_login(self):
        # build the authorization token request
        tokenpost = {
            'tenant_id' : self.tenant_id,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': self.grant_type,
            'resource': self.domain
        }
        # make the login request
        try:
            response = requests.post(self.login_url, data=tokenpost)
        except Exception as e:
            msg = "Login request received exception: {0}".format(e)
            logger.error(msg)
            raise Exception(msg)

        # check the response code
        if response.status_code != 200:
            msg = "Login request could not get access token. STATUS_CODE: {0}, URL: {1}, MESSAGE: {2}".format(
                response.status_code, response.url, response.text)
            logger.error(msg)
            raise Exception(msg)
        else:
            pacctok = response.json().get('access_token')
            self.set_access_token(pacctok)
            logger.info("Login request obtained access token.")
            return {
                'status': 'success',
                'access_token': pacctok,
            }

    #
    # Method to make the request, receives the different methods (post, delete, patch, get) that the api allows,
    # see the documentation to check how to use the filters:
    # https://msdn.microsoft.com/en-us/library/gg309461(v=crm.7).aspx
    #
    def make_request(
        self,
        method,
        endpoint,
        expand=None,
        filter=None,
        orderby=None,
        select=None,
        skip=None,
        top=None,
        data=None,
        json=None,
        **kwargs,
    ):
        extra = {}
        if expand is not None and isinstance(expand, str):
            extra["$expand"] = str(expand)
        if filter is not None and isinstance(filter, str):
            extra["$filter"] = filter
        if orderby is not None and isinstance(orderby, str):
            extra["$orderby"] = orderby
        if select is not None and isinstance(select, str):
            extra["$select"] = select
        if skip is not None and isinstance(skip, str):
            extra["$skip"] = skip
        if top is not None and isinstance(top, str):
            extra["$top"] = str(top)

        assert self.domain is not None, "'domain' is required"
        assert self.access_token is not None, "You must provide a 'token' to make requests"
        url = f"{self.domain}/{self.api_path}/{endpoint}?" + urlencode(extra)
        msg = "Make request method: {0} url: {1} json: {2}".format(method, unquote_plus(url), json)
        logger.info(msg)
        try:
            if method == "get":
                response = requests.request(method, url, headers=self.headers, params=kwargs)
            else:
                response = requests.request(method, url, headers=self.headers, data=data, json=json)
        except Exception as e:
            msg = "Make request received exception: {0}".format(e)
            logger.error(msg)
            raise Exception(msg)

        return self.parse_response(response)

    #
    # Wrapper to make get request.
    #
    def _get(self, endpoint, data=None, **kwargs):
        return self.make_request("get", endpoint, data=data, **kwargs)

    #
    # Wrapper to make post request.
    #
    def _post(self, endpoint, data=None, json=None, **kwargs):
        return self.make_request("post", endpoint, data=data, json=json, **kwargs)

    #
    # Wrapper to make delete request.
    #
    def _delete(self, endpoint, **kwargs):
        return self.make_request("delete", endpoint, **kwargs)

    #
    # Wrapper to make patch request.
    #
    def _patch(self, endpoint, data=None, json=None, **kwargs):
        return self.make_request("patch", endpoint, data=data, json=json, **kwargs)

    #
    # Parse the response and provide the json data if successful or raise exception
    #
    def parse_response(self, response):
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 204 or response.status_code == 201:
            if 'OData-EntityId' in response.headers:
                entity_id = response.headers['OData-EntityId']
                if entity_id[-38:-37] == '(' and entity_id[-1:] == ')':  # Check container
                    guid = entity_id[-37:-1]
                    guid_pattern = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
                    if guid_pattern.match(guid):
                        return guid
                    else:
                        return True  # Not all calls return a guid
            else:
                return True
        else:
            msg = "Request received error. STATUS_CODE: {0}, URL: {1}, MESSAGE: {2}".format(
                response.status_code, response.url, response.text)
            logger.error(msg)
            raise Exception(msg)

    #
    # Generic methods to operate on the entity type data.
    #
    def get_data(self, type=None, **kwargs):
        if type is not None:
            return self._get(type, **kwargs)
        msg = "A type is necessary. Example: contacts, leads, accounts, etc... check the library"
        logger.error(msg)
        raise Exception(msg)

    def create_data(self, type=None, params=None):
        if type is not None:
            if params is not None and isinstance(params, dict):
                return self._post(type, json=params)
            else:
                msg = "params needs to be a dict"
                logger.error(msg)
                raise Exception(msg)
        msg = "A type is necessary. Example: contacts, leads, accounts, etc... check the library"
        logger.error(msg)
        raise Exception(msg)

    def update_data(self, type=None, id=None, params=None):
        if type is not None and id is not None:
            url = "{0}({1})".format(type, id)
            if params is not None and isinstance(params, dict):
                return self._patch(url, json=params)
            else:
                msg = "params needs to be a dict"
                logger.error(msg)
                raise Exception(msg)
        msg = "A type is necessary. Example: contacts, leads, accounts, etc... check the library"
        logger.error(msg)
        raise Exception(msg)

    def delete_data(self, type=None, id=None):
        if type is not None and id is not None:
            return self._delete("{0}({1})".format(type, id))
        msg = "A type is necessary. Example: contacts, leads, accounts, etc... check the library"
        logger.error(msg)
        raise Exception(msg)

    #
    # contact section, see the documentation
    # https://docs.microsoft.com/es-es/dynamics365/customer-engagement/web-api/contact?view=dynamics-ce-odata-9
    #
    def get_contacts(self, **kwargs):
        return self._get("contacts", **kwargs)

    def create_contact(self, params):
        if params is not None and isinstance(params, dict):
            return self._post("contacts", json=params)
        else:
            msg = "params needs to be a dict"
            logger.error(msg)
            raise Exception(msg)

    def delete_contact(self, id):
        if id != "":
            return self._delete("contacts({0})".format(id))
        msg = "ID is required to delete a contact"
        logger.error(msg)
        raise Exception(msg)

    def update_contact(self, id, params):
        if id != "":
            url = "contacts({0})".format(id)
            if params is not None and isinstance(params, dict):
                return self._patch(url, json=params)
            else:
                msg = "params needs to be a dict"
                logger.error(msg)
                raise Exception(msg)
        msg = "ID is required to update a contact"
        logger.error(msg)
        raise Exception(msg)

    #
    # account section, see the documentation
    # https://docs.microsoft.com/es-es/dynamics365/customer-engagement/web-api/account?view=dynamics-ce-odata-9
    #
    def get_accounts(self, **kwargs):
        return self._get("accounts", **kwargs)

    def create_account(self, params):
        if params is not None and isinstance(params, dict):
            return self._post("accounts", json=params)
        else:
            msg = "params needs to be a dict"
            logger.error(msg)
            raise Exception(msg)

    def delete_account(self, id):
        if id != "":
            return self._delete("accounts({0})".format(id))
        msg = "ID is required to delete an account"
        logger.error(msg)
        raise Exception(msg)

    def update_account(self, id, params):
        if id != "":
            url = "accounts({0})".format(id)
            if params is not None and isinstance(params, dict):
                return self._patch(url, json=params)
            else:
                msg = "params needs to be a dict"
                logger.error(msg)
                raise Exception(msg)
        msg = "ID is required to update an account"
        logger.error(msg)
        raise Exception(msg)

    #
    # opportunity section, see the documentation
    # https://docs.microsoft.com/es-es/dynamics365/customer-engagement/web-api/opportunity?view=dynamics-ce-odata-9
    #
    def get_opportunities(self, **kwargs):
        return self._get("opportunities", **kwargs)

    def create_opportunity(self, params):
        if params is not None and isinstance(params, dict):
            return self._post("opportunities", json=params)
        else:
            msg = "params needs to be a dict"
            logger.error(msg)
            raise Exception(msg)

    def delete_opportunity(self, id):
        if id != "":
            return self._delete("opportunities({0})".format(id))
        msg = "ID is required to delete an opportunity"
        logger.error(msg)
        raise Exception(msg)

    def update_opportunity(self, id, params):
        if id != "":
            url = "opportunities({0})".format(id)
            if params is not None and isinstance(params, dict):
                return self._patch(url, json=params)
            else:
                msg = "params needs to be a dict"
                logger.error(msg)
                raise Exception(msg)
        msg = "ID is required to update an opportunity"
        logger.error(msg)
        raise Exception(msg)

    #
    # leads section, see the documentation
    # https://docs.microsoft.com/es-es/dynamics365/customer-engagement/web-api/lead?view=dynamics-ce-odata-9
    #
    def get_leads(self, **kwargs):
        return self._get("leads", **kwargs)

    def create_lead(self, params):
        if params is not None and isinstance(params, dict):
            return self._post("leads", json=params)
        else:
            msg = "params needs to be a dict"
            logger.error(msg)
            raise Exception(msg)

    def update_lead(self, id, params):
        if id != "":
            url = "leads({0})".format(id)
            if params is not None and isinstance(params, dict):
                return self._patch(url, json=params)
            else:
                msg = "params needs to be a dict"
                logger.error(msg)
                raise Exception(msg)
        msg = "ID is required to update a lead"
        logger.error(msg)
        raise Exception(msg)

    def delete_lead(self, id):
        if id != "":
            return self._delete("leads({0})".format(id))
        msg = "ID is required to delete a lead"
        logger.error(msg)
        raise Exception(msg)

    #
    # campaign section, see the documentation
    # https://docs.microsoft.com/es-es/dynamics365/customer-engagement/web-api/campaign?view=dynamics-ce-odata-9
    #
    def get_campaigns(self, **kwargs):
        return self._get("campaigns", **kwargs)

    def create_campaign(self, params):
        if params is not None and isinstance(params, dict):
            return self._post("campaigns", json=params)
        else:
            msg = "params needs to be a dict"
            logger.error(msg)
            raise Exception(msg)

    def update_campaign(self, id, params):
        if id != "":
            url = "campaigns({0})".format(id)
            if params is not None and isinstance(params, dict):
                return self._patch(url, json=params)
            else:
                msg = "params needs to be a dict"
                logger.error(msg)
                raise Exception(msg)
        msg = "ID is required to update a campaign"
        logger.error(msg)
        raise Exception(msg)

    def delete_campaign(self, id):
        if id != "":
            return self._delete("campaigns({0})".format(id))
        msg = "ID is required to delete a campaign"
        logger.error(msg)
        raise Exception(msg)

if __name__ == "__main__":

    # NOTE: Ensure that logs/ directory is present, else will get an error while running.
    logging.basicConfig(filename='logs/azuredynamicsclient.log',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(module)s.%(funcName)s:%(lineno)d %(message)s')

    # Read the env variables necessary to retrieve the oauth token.
    # Refer to readme.md file for details.
    tenant_id       = os.environ["SCR_CRM_TENANT_ID"]
    client_id       = os.environ["SCR_CRM_CLIENT_ID"]
    client_secret   = os.environ["SCR_CRM_CLIENT_SECRET"]
    domain          = os.environ["SCR_CRM_DOMAIN"]
    login_url       = os.environ["SCR_CRM_LOGIN_URL"]
    grant_type      = "client_credentials"

    # Create the crm client. access_token is setup in the do_login step.
    crmclient = AzureDynamicsClient(domain=domain, tenant_id=tenant_id,
                    client_id=client_id, client_secret=client_secret,
                    login_url=login_url, grant_type=grant_type, access_token=None)

    # Do the login to set the access token.
    resp = crmclient.do_login()
    if resp['status'] == "success":
        ############## contacts operations ######################
        # Perform get contacts
        print("Getting contacts...[contactid] - [fullname]")
        crmresults = crmclient.get_contacts()
        # Loop through it
        for x in crmresults['value']:
            print (x['contactid'] + ' - ' + x['fullname'])

        # Perform a create contact
        print("\nCreating contact...[firstname:test fname]")
        contact_data = {"firstname": "test fname",
                        "lastname": "test lname",
                        "middlename": "test mname",
                        "emailaddress1": "testcontact@test.com",
                        "telephone1": "654-321-0123"}
        # Store created contactid for further uses
        pcontactid = crmclient.create_contact(contact_data)
        print("Result created contactid:", pcontactid)

        # Perform a get contact with select fields
        print("\nGetting contacts with select fields...[firstname] - [telephone1]")
        crmresults = crmclient.get_contacts(select="firstname,telephone1")
        # Loop through it
        for x in crmresults['value']:
            print (x['contactid'] + ' - ' + x['firstname'] + ' - ' + x['telephone1'])

        # Perform a get contact with filter
        print("\nGetting filtered contact...[contactid], select fields [firstname] - [telephone1]")
        filterstr = f"contactid eq {pcontactid}"
        crmresults = crmclient.get_contacts(filter=filterstr,
                                            select="firstname,telephone1")
        # Loop through it
        for x in crmresults['value']:
            print (x['contactid'] + ' - ' + x['firstname'] + ' - ' + x['telephone1'])

        # Perform an update contact
        print("\nUpdating contact...[contactid] - [telephone1 654-777-7777]")
        updcontact_data = {"telephone1": "654-777-7777"}
        crmresults = crmclient.update_contact(id=pcontactid, params=updcontact_data)
        print("Result:", crmresults)

        # Perform a get contact with filter
        print("\nGetting filtered contact...[contactid], select fields [firstname] - [telephone1]")
        filterstr = f"contactid eq {pcontactid}"
        crmresults = crmclient.get_contacts(filter=filterstr,
                                            select="firstname,telephone1")
        # Loop through it
        for x in crmresults['value']:
            print (x['contactid'] + ' - ' + x['firstname'] + ' - ' + x['telephone1'])

        # Perform a delete contact
        print("\nDeleting contact...[contactid]")
        crmresults = crmclient.delete_contact(id=pcontactid)
        print("Result:", crmresults)

        ############## leads operations ######################
        # Perform a sample get leads
        print("\nGetting leads...[fullname] - [leadid] - [subject]")
        crmresults = crmclient.get_leads()
        # Loop through it
        for x in crmresults['value']:
            print (x['fullname'] + ' - ' + x['leadid'] + ' - ' + x['subject'])

    else:
        print("Unable to login.")
