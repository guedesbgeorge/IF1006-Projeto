from flask import Flask
from flask import request
from flask import json
from flask import jsonify
from random import randint

import action_builder
from builder_wrapper import BuilderWrapper
import os

app = Flask(__name__)
bws = {}

# route_suffix = str(randint(0,1000000))
route_suffix = "832555"
rout = 'http://c1551687.ngrok.io'
os.environ['WEB_HOOK_ROUTE'] = rout+"/webhook"+route_suffix


@app.route('/webhook'+route_suffix, methods=['POST'])
def webhook():
    input_json = request.get_json()
#    print("json --> " + str(json))
    print("Incoming hook detected!")
    print("X-GitHub-Event: " + str(request.headers['X-GitHub-Event']))
    print("X-GitHub-Delivery: " + str(request.headers['X-GitHub-Delivery']))
    print("Json: " + str(json.dumps(input_json)))

    repository_name = input_json['repository']['full_name']
    curr_commit = input_json['after']
    is_master = input_json['ref'].endswith("master")

    print("Repository:" + repository_name)
    print("Curr commit: " + curr_commit)
    print("is_master:  " + str(is_master))

    bw = bws[repository_name]
    if is_master:
        action_builder.build(bw)

    return 'Hook handled'

@app.route('/register', methods=['POST'])
def register():
    json = request.get_json()
    git_api_key = json['git_api_key']
    docker_hub_key = json['docker_hub_key']
    google_cloud_key = json['google_cloud_key']
    repository_name = json['repository_name']

    hook_id = None
    if json.__contains__('hook_id'):
        hook_id = json['hook_id']

    print ("Creating builder")
    bw = BuilderWrapper(git_api_key=git_api_key, docker_hub_key=docker_hub_key, google_cloud_key=google_cloud_key, repository_name=repository_name, hook_id=hook_id)

    print ("Builder created!")
    bw.print_config()
    bws['repository_name'] = bw


    print("repo hook: " + str(bw.project.hook))
    return 'Builder created with success'


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'watched by mr4s'



