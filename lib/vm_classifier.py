from lib.credential import Credential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient

class VMClassifier(object):

    def __init__(self):
        # Login into Azure using Service Principal credentials from config.py
        self._credential = Credential().get()
        # Get all subscription IDs visible by the Service Principal
        self._subscription_ids = [x.subscription_id for x in SubscriptionClient(self._credential).subscriptions.list()]

    def classify(self,fqdn: str):
        node_shortname = fqdn.split(".")[0].lower()
        # Search the VM in every subscription
        for id in self._subscription_ids:
            resource_management_client = ResourceManagementClient(self._credential,id)    
            # We search the VMs which name contains the Puppet Node shortname
            filtered_vms = resource_management_client.resources.list(
                filter = f"substringOf('{node_shortname}',name) and resourceType eq 'Microsoft.Compute/virtualMachines'"
            )
            # If there is one VM in the list
            for vm in filtered_vms:
                # We store the values from puppet_environment and puppet_classes tags
                environment = vm.tags['puppet_environment'] if 'puppet_environment' in vm.tags else None
                classes = vm.tags['puppet_classes'].split(",") if 'puppet_classes' in vm.tags else []
                # Prepare the output dict with default values
                output = {
                    'classes':None, 
                    'environment': environment if environment is not None else 'production'
                }
                # Store each class as a dict key with None value
                for cl in classes:
                    if output['classes'] is None:
                        output['classes'] = {}
                    output['classes'][cl.strip()]=None
                
                return output
            
        return None