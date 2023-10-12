"""ENC that generates environment and puppet classes from Azure Tags of the VM"""

import sys
from lib.credential import Credential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import yaml

# This dumper modifies 'null' with blanks to ensure Puppet-compatible YAML format
yaml.SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
  )

# There must be one parameter. If there are more, the rest are ignored
if len(sys.argv) < 2:
    sys.exit(1)
 
# Received parameter is FQDN of the host as stored by Puppet
node_fqdn = sys.argv[1]

# Store the shortname of the host
node_shortname = node_fqdn.split(".")[0].lower()

# Login into Azure using Service Principal credentials from config.py
credential = Credential().get()

# Get all subscription IDs visible by the Service Principal
subscription_ids = [x.subscription_id for x in SubscriptionClient(credential).subscriptions.list()]

# Search the VM in every subscription
for id in subscription_ids:
    resource_management_client = ResourceManagementClient(credential,id)    
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
        # Dump the information as YAML to standard output
        yaml.safe_dump(output, sys.stdout,default_flow_style=False)

        # Return 0 code (OK)
        sys.exit(0)

# If we reach this, no VM has been found in Azure, return 1 code (ERROR)
sys.exit(1)

        