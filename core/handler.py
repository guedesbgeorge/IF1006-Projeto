from flask import Flask
from flask import request
from flask import json
from flask import jsonify
from random import randint

from action_builder import ActionBuilder
from docker_api import DockerAPI
from builder_wrapper import BuilderWrapper
import os

app = Flask(__name__)
bws = {}
DockerAPI.init()


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
#    print("Json: " + str(json.dumps(input_json)))

    repository_name = input_json['repository']['full_name']
    curr_commit = input_json['after']
    is_master = input_json['ref'].endswith("master")

    print("Repository:" + repository_name)
    print("Curr commit: " + curr_commit)
    print("is_master:  " + str(is_master))

    bw = bws[repository_name]
    if is_master:
        print ("Commit on master detected!")
        try:
            pipeline_results = ActionBuilder.start_pipeline(bw)

            print ("Pipeline results | Number of runned steps:" + str(pipeline_results.__len__()))
            for result in pipeline_results:
                if result.has_failed():
                    print ("[Failed] Namespace: " + str(result.namespace))

                    print ("Error:\n" + str(result.get_error_msg()))
                else:
                    print ("[Successed] Namespace: " + str(result.namespace))
                    print ("Message:\n" + result.get_message())
        finally:
            bw.erase_repo()

    return 'Hook handled'

@app.route('/register', methods=['POST'])
def register():
    json = request.get_json()
    git_api_key = json['git_api_key']
    docker_hub_u = json['docker_hub_u']
    docker_hub_p = json['docker_hub_p']
    google_cloud_key = json['google_cloud_key']
    repository_name = json['repository_name']
    print ("oi!")
    if bws.__contains__(repository_name) is False:
        hook_id = None
        if json.__contains__('hook_id'):
            hook_id = json['hook_id']

        print ("Creating builder")
        bw = BuilderWrapper(git_api_key=git_api_key, docker_hub_u=docker_hub_u, docker_hub_p=docker_hub_p, google_cloud_key=google_cloud_key, repository_name=repository_name, hook_id=hook_id)

        print ("Builder created!")
        bw.print_config()
        bws[repository_name] = bw

        print("repo hook: " + str(bw.project.hook))
        return 'Builder created with success'
    else:
        return "Builder already exists"



@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'watched by mr4s'



