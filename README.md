# enc-azure-tags

External Node Classifier for Puppet that retrieves environment and classes from Azure VM Tags

# Prerrequisites

* (Puppet Server) Python 3.8+
* An Azure Service Principal with enough permissions to query the Resource Manager and to retrieve VM tags. You can find more information about creating a Service Principal [here](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)

# How it works

ENCs are programs that receive one argument (the Puppet Agent node name) and return a YAML into stdout with the information about the environment and classes that must be applied to that node in the Puppet Agent run. This repo provides a simple Python script that receives the Puppet Agent node name (usually a FQDN) and tries to match that FQDN with a VM name from Azure subscriptions that are visible to the Service Principal that is used to run the Azure queries. So there are two important caveats:

* Your VM's Operating System name must be a substring of the VM Name in Azure
* Your VM Names in Azure must be unique across all the subscriptions that the Service Principal can query

Failing to meet these two requisites may cause that the ENC retrieves information from a VM that is not the one the which is running the Puppet Agent.

To classify the nodes you must provision two tags into the Azure VM:

* `puppet_environment`: Name of the environment for the VM. If not present defaults to `production`
* `puppet_classes`: comma-separated list of Puppet classes that must be applied to this VM, e.g. `linux::base, role::mysql`. If not present defaults to empty (no classes)

There are two flavours of this ENC:

* CLI Mode: runs as standalone command line application and can be used directly from Puppet Servers with Python installed
* REST Mode: runs as a HTTP Server and can be called remotely

# CLI Mode

## Installation

This process has to be done with the `puppet` user, or the user that runs the Puppet Server process in every Puppet Server node

First, clone this repo into your Puppet Server node:

```
$ cd /etc/puppetlabs/code
$ git clone https://github.com/cpiment/enc-azure-tags
$ cd enc-azure-tags
``` 

Then copy `config.py.SAMPLE` into `config.py`

```
$ cp config.py.SAMPLE config.py
```

Edit `config.py` and set the values with the credentials of the Service Principal

```
CONFIG = {
    "SERVICE_PRINCIPAL_CLIENT_ID": 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    "SERVICE_PRINCIPAL_CLIENT_SECRET": '*****************************',
    "SERVICE_PRINCIPAL_TENANT_ID": 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy'
}
```

Or if your Service Principal password is stored in a Keyvault

```
CONFIG = {
    "SERVICE_PRINCIPAL_CLIENT_ID": 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    "SERVICE_PRINCIPAL_TENANT_ID": 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy',
    "SERVICE_PRINCIPAL_CLIENT_SECRET_KEYVAULT": 'https://***.vault.azure.net/secrets/my-sp-password'
}
```

You can also specify an Azure Managed Identity ID to retrieve the password using `AZURE_CLIENT_ID` in the config.py file

Create a python virtual environment named `venv`, activate it and install the required packages

```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Configure your Puppet Server's `puppet.conf` to use the ENC and restart it:

```
[master]
  node_terminus = exec
  external_nodes = /etc/puppetlabs/code/enc-azure-tags/enc-azure-tags
```

## Testing

Once you have completed the `Installation` steps, you can test the script manually running it with a FQDN:

```
$ /etc/puppetlabs/code/enc-azure-tags/enc-azure-tags mymachine.local
classes:
  base::windows:
  role::iis:
environment: test
```

If you don't have a Service Principal you can test the script without a `config.py` file and it will try to use you Azure CLI credentials. So you have to do `az login` beforehand.

# REST Mode

Based on [ncsa/puppet-enc](https://github.com/ncsa/puppet-enc/tree/main), it starts a Flask application which receives the requests from the ENC in Puppet Servers.

## Configure Puppet Server

First of all, copy the `enc-azure-rest` file to a location of your Puppet Server, e.g. `/etc/puppetlabs/code/enc-azure-tags/enc-azure-rest`, and be sure that it has execution permissions for the `puppet` user:

```
chmod +x /etc/puppetlabs/code/enc-azure-tags/enc-azure-rest
```

Be sure to modify `ENDPOINT` variable in `enc-azure-rest` to the endpoint where you are going to deploy the REST ENC server

Configure your Puppet Server's `puppet.conf` to use the ENC REST client and restart it:

```
[master]
  node_terminus = exec
  external_nodes = /etc/puppetlabs/code/enc-azure-tags/enc-azure-rest
```

##  Deploy REST Mode on a server using Python

First, clone this repo into any server:

```
$ cd /etc/puppetlabs/code
$ git clone https://github.com/cpiment/enc-azure-tags
$ cd enc-azure-tags
``` 

Then copy `config.py.SAMPLE` into `config.py`

```
$ cp config.py.SAMPLE config.py
```

Edit `config.py` and set the values with the credentials of the Service Principal

```
CONFIG = {
    "SERVICE_PRINCIPAL_CLIENT_ID": 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    "SERVICE_PRINCIPAL_CLIENT_SECRET": '*****************************',
    "SERVICE_PRINCIPAL_TENANT_ID": 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy'
}
```

Or if your Service Principal password is stored in a Keyvault

```
CONFIG = {
    "SERVICE_PRINCIPAL_CLIENT_ID": 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
    "SERVICE_PRINCIPAL_TENANT_ID": 'yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy',
    "SERVICE_PRINCIPAL_CLIENT_SECRET_KEYVAULT": 'https://***.vault.azure.net/secrets/my-sp-password'
}
```

You can also specify an Azure Managed Identity ID to retrieve the password using `AZURE_CLIENT_ID` in the config.py file

Create a python virtual environment named `venv`, activate it and install the required packages

```
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements-rest.txt
```

Start the REST server:

```
waitress-serve enc_azure_tags_rest:app
```

By default it will listen on any IP address of the server and port 8080

### Testing

Use `curl` to test:

```
curl http://localhost:8080/enc/hosts/mymachine.local
```

## Deploy REST Mode on a server using Docker/Podman

I have used `podman` but you can use the same commands with `docker`

First, clone this repo into any server with `docker` or `podman`:

```
$ cd /etc/puppetlabs/code
$ git clone https://github.com/cpiment/enc-azure-tags
$ cd enc-azure-tags
``` 

Build the image

```
podman build -t enc-azure-tags-rest:1.0 .
```

Run the image using the necessary environment variables, e.g.:

```
podman run \
  -p 8080:8080 \
  --name enc-azure-tags \
  --rm \
  --env SERVICE_PRINCIPAL_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx \
  --env SERVICE_PRINCIPAL_TENANT_ID='yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy' \
  --env SERVICE_PRINCIPAL_CLIENT_SECRET_KEYVAULT=https://***.vault.azure.net/secrets/my-sp-password \
  enc-azure-tags-rest:1.0
```

You can specify `SERVICE_PRINCIPAL_CLIENT_SECRET` instead of retrieving it from a Key Vault

### Testing

Use `curl` to test:

```
curl http://localhost:8080/enc/hosts/mymachine.local
```

# Contributing

Feel free to open issues or open PR's, they will be reviewed as soon as possible