"""Credential clas to retrieve a credential object to be used in operations"""
from azure.identity import AzureCliCredential, ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.keyvault.secrets import SecretClient
from lib.print_ts import print_ts
from urllib.parse import urlsplit
try:
    from config import CONFIG
except ImportError:
    from os import environ as CONFIG

class Credential(object):
    def __init__(self):
        try:
            # If CLIENT_ID and TENANT_ID in the environment variables
            if 'SERVICE_PRINCIPAL_CLIENT_ID' in CONFIG \
                and 'SERVICE_PRINCIPAL_TENANT_ID' in CONFIG:
                """ If we have CLIENT_ID and TENANT_ID we can get the password from two sources:
                        - From the environment as SERVICE_PRINCIPAL_CLIENT_SECRET environment variable
                        - From a Key Vault, with the secret URL in SERVICE_PRINCIPAL_CLIENT_SECRET_KEYVAULT environment variable
                """
                # If password in environment, we retrieve it
                if 'SERVICE_PRINCIPAL_CLIENT_SECRET' in CONFIG:
                    sp_password = CONFIG['SERVICE_PRINCIPAL_CLIENT_SECRET']
                    #print_ts('Using Service Principal')
                # If we have the KeyVault URL
                elif ('SERVICE_PRINCIPAL_CLIENT_SECRET_KEYVAULT' in CONFIG):
                    # Split the URL because to use it we have to provide the base URL to the Secret Client
                    parts = urlsplit(CONFIG['SERVICE_PRINCIPAL_CLIENT_SECRET_KEYVAULT'])
                    # Generate the base URL
                    key_vault_url = parts.scheme + "://" + parts.netloc
                    # Generate the SecretClient to retrieve the secret using the "DefaultAzureCredential"
                    #  If a User Managed Identity is configured, the ID must be passed on AZURE_CLIENT_ID
                    secret_client_params = {
                        "exclude_developer_cli_credential" : True,
                        "exclude_cli_credential": True,
                        "exclude_visual_studio_code_credential": True,
                        "exclude_interactive_browser_credential": True
                    }
                    if 'AZURE_CLIENT_ID' in CONFIG:
                        secret_client_params['client_id'] = CONFIG['AZURE_CLIENT_ID']

                    secret_client = SecretClient(vault_url=key_vault_url,
                                                 credential=DefaultAzureCredential(**secret_client_params)
                                                )
                    # We retrieve the password using the last piece of the URL path as secret name
                    sp_password = secret_client.get_secret(name=parts.path.split("/")[-1]).value
                    #print_ts('Using Service Principal with password from KeyVault')
                else:
                    #print_ts('Missing necessary environment variables')
                    raise Exception('Missing necessary configuration')
                # Change to Service Principal when we have it
                self.credential = ClientSecretCredential(
                    client_id=CONFIG['SERVICE_PRINCIPAL_CLIENT_ID'],
                    client_secret=sp_password,
                    tenant_id=CONFIG['SERVICE_PRINCIPAL_TENANT_ID']
                )
            # If environment variables are clean, we try to login into Azure using Azure CLI credentials
            else:
                #print_ts('Using Azure CLI credential')
                self.credential = AzureCliCredential()
        except Exception as exc:
            #print_ts("Before continuing you must do `az login`")
            raise Exception(exc)
    
    def get(self):
        subscription_client = SubscriptionClient(self.credential)
        # This loop is done to raise exception if credentials are invalid
        list = [x for x in subscription_client.subscriptions.list()]
        return self.credential
