""" Based on https://github.com/ncsa/puppet-enc which is BSD-Licensed

BSD 3-Clause License

Copyright (c) 2023, NCSA

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from flask import Flask, request, abort, Response
import yaml
from lib.vm_classifier import VMClassifier

# Init the VM Classifier
classifier = VMClassifier()

app = Flask(__name__)

# This dumper modifies 'null' with blanks to ensure Puppet-compatible YAML format
yaml.SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
  )

def make_response(data):
    """Create yaml response."""
    if data:
        resp = Response(response=yaml.safe_dump(data,default_flow_style=False), status=200,  mimetype="text/yaml")
    else:
        resp = Response(response="", status=200, mimetype="text/yaml")
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/healthz")
def root():
    return "OK"

@app.route("/hosts/<fqdn>", methods=['GET'])
def get_host(fqdn):
    host = classifier.classify(fqdn)
    if host is not None:
        return make_response(host)

    return make_response(None)

if __name__ == '__main__':
    app.run(debug=True)