# Scribbledata.io Azure Dynamics Client

## Useful tutorials to setup Azure and Dynamics365 for web api access

https://ei.docs.wso2.com/en/latest/micro-integrator/references/connectors/microsoft-dynamics365-connector/microsoft-dynamics365-configuration/  
  
https://www.youtube.com/watch?v=wZQ64yaDK84  

## Steps to setup and run the Dynamics365 Sales instance

Sign up for the free trial  
https://dynamics.microsoft.com/en-us/dynamics-365-free-trial/  
Choose the Dynamics365 Sales - Try for free > 

## Steps to setup and run the azuredynamics client

1. Create the python virtual env with the correct version of python.  
 $ python3.9 -m venv venv

2. Activate the virtual environment.  
 $ source venv/bin/activate

3. Install the dependencies.  
The dynamics client uses the requests package which is already installed when enrichsdk is installed. In case it is being run separately then one can create requirements.txt with the requests package mentioned in it and install using:  
 $ pip install -r requirements.txt

4. Setup the credentials needed to connect to the msdynamics365 sales installation. Create the .env.dynamics file as shown below with the environment variables. This file is not committed to git and is mentioned in .gitignore. Sample values are shown below. Please contact the administrator for values.

```
$ cat .env.dynamics
#!/bin/bash
# Set these values to retrieve the oauth token
# For Linux use:
export SCR_CRM_TENANT_ID=fc2dxxxx-xxxx-xxxx-ad07-xxxxxxxx4813
export SCR_CRM_CLIENT_ID=535exxxx-xxxx-xxxx-8cc3-xxxxxxxxc9e6
export SCR_CRM_CLIENT_SECRET=TMXxxxxxxxxxxEaPxxxxxxxxxxfYJdxxxxxxxxmx
export SCR_CRM_DOMAIN=https://org03xxxxxx.crm8.dynamics.com
export SCR_CRM_LOGIN_URL=https://login.microsoftonline.com/fc2dxxxx-xxxx-xxxx-ad07-xxxxxxxx4813/oauth2/token
```

5. Set the environment variables.  
 $ source .env.dynamics

6. Run the sample program which uses the client library.  
 $ python azuredynamicsclient.py

7. Logs can be seen in the logs/azuredynamicsclient.log file

8. In the browser where you have logged in to the Dynamics365 Sales, you can perform sample get calls for the entities. As an example:   
https://org03xxxxxx.api.crm8.dynamics.com/api/data/v9.2/leads  
