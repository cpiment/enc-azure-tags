"""ENC that generates environment and puppet classes from Azure Tags of the VM"""

import sys
from lib.vm_classifier import VMClassifier
import yaml

# This dumper modifies 'null' with blanks to ensure Puppet-compatible YAML format
yaml.SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
  )

# There must be one parameter. If there are more, the rest are ignored
if len(sys.argv) < 2:
    sys.exit(1)

# Init the VM Classifier
classifier = VMClassifier()

# Received parameter is FQDN of the host as stored by Puppet
node_fqdn = sys.argv[1]

# Classify the VM
output = classifier.classify(node_fqdn)

if output is not None:
    # Dump the information as YAML to standard output
    yaml.safe_dump(output, sys.stdout,default_flow_style=False)

    # Return 0 code (OK)
    sys.exit(0)

# If we reach this, no VM has been found in Azure, return 1 code (ERROR)
sys.exit(1)

        