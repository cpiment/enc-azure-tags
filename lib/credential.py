"""Credential clas to retrieve a credential object to be used in operations"""
from azure.identity import AzureCliCredential, ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from lib.print_ts import print_ts
try:
    from config import CONFIG
except ImportError:
    from os import environ as CONFIG

class Credential(object):
    def __init__(self):
        try:
            if 'SERVICE_PRINCIPAL_CLIENT_ID' in CONFIG \
                and 'SERVICE_PRINCIPAL_CLIENT_SECRET' in CONFIG \
                and 'SERVICE_PRINCIPAL_TENANT_ID' in CONFIG:

                #print_ts('Using Service Principal')
                # Change to Service Principal when we have it
                self.credential = ClientSecretCredential(
                    client_id=CONFIG['SERVICE_PRINCIPAL_CLIENT_ID'],
                    client_secret=CONFIG['SERVICE_PRINCIPAL_CLIENT_SECRET'],
                    tenant_id=CONFIG['SERVICE_PRINCIPAL_TENANT_ID']
                )
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
