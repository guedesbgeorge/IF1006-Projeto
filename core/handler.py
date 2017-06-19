from flask import Flask, request, json, jsonify, send_from_directory
from random import randint
from subprocess import call
from action_builder import ActionBuilder
from docker_api import DockerAPI
from builder_wrapper import BuilderWrapper
from builder_wrapper import GCloudConfig
from google_cloud import GCloudAPI

import json
from results_output_generator import OutputGenerator
import os

app = Flask(__name__)
bws = {}
DockerAPI.init()


# route_suffix = str(randint(0,1000000))
route_suffix = "934644"
os.environ['WEB_HOOK_ROUTE'] =  os.environ['WEB_HOOK_HOST']+"/webhook"+route_suffix
print("Hook Route: " + os.environ['WEB_HOOK_ROUTE'])


GCLOUD_PATH = "google_cloud_keys"
call(["mkdir", "-p", GCLOUD_PATH])

OutputGenerator.init_outputs_folder()



@app.route('/webhook'+route_suffix, methods=['POST'])
def webhook():

    print("Hook Route: " + os.environ['WEB_HOOK_ROUTE'])

    input_json = request.get_json()
#    print("json --> " + str(json))
    print("Incoming hook detected!")
    event = str(request.headers['X-GitHub-Event'])
    print("X-GitHub-Event: " + event)
    print("X-GitHub-Delivery: " + str(request.headers['X-GitHub-Delivery']))
#    print("Json: " + str(json.dumps(input_json)))



    if event == "ping":
        return "ping detected"

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
            DockerAPI.login(username=bw.secrets.docker_hub_u, password=bw.secrets.docker_hub_p)

            OutputGenerator.generate_loading_markup(bw)
            pipeline_results = ActionBuilder.start_pipeline(bw)
            print ("Pipeline results | Number of runned steps:" + str(pipeline_results.__len__()))
            for result in pipeline_results:
                if result.has_failed():
                    print ("[Failed] Namespace: " + str(result.namespace))

                    print ("Error:\n" + str(result.get_error_msg()))
                else:
                    print ("[Successed] Namespace: " + str(result.namespace))
                    print ("Message:\n" + result.get_message())
            bw.count += 1
        finally:
            bw.erase_repo()

    return 'Hook handled'

@app.route('/setgcloudfile', methods=['POST'])
def setcloudfile():
    json = request.get_json()

    print("JSON: " + str(json))

    repository_name = json["repository_name"]
    bw = bws[repository_name]
    gcloud_key_file = create_file_for_google_cloud_key(json, repository_name=repository_name)

    bw.gcloud_config.key_file = gcloud_key_file
    print("GCloud key file now is: " + bw.gcloud_config.key_file)

    print("Activating google cloud service")
    GCloudAPI.activate_service(bw.gcloud_config)

    return "Google Cloud config activated"

@app.route('/register', methods=['POST'])
def register():
    json = request.get_json()
    git_api_key = json['git_api_key']
    docker_hub_u = json['docker_hub_u']
    docker_hub_p = json['docker_hub_p']

    gcloud_project = json['gcloud_config']['project']
    gcloud_instance = json['gcloud_config']['instance']
    gcloud_zone = json['gcloud_config']['zone']
    gcloud_user = json['gcloud_config']['user']

    repository_name = json['repository_name']
    print ("oi!")
    if bws.__contains__(repository_name) is False:
        hook_id = None
        if json.__contains__('hook_id'):
            hook_id = json['hook_id']

        print ("Creating builder")
        bw = BuilderWrapper(git_api_key=git_api_key, docker_hub_u=docker_hub_u, docker_hub_p=docker_hub_p,  repository_name=repository_name, hook_id=hook_id)

#        print("HOOKs: " + str(bw.project.repo.get_hooks().get_page(0)))
#        bw.project.repo.get_hook(14430897).delete()
#        bw.project.repo.get_hook(14452288).delete()
#        bw.project.repo.get_hook(14452038).delete()
#        bw.project.repo.get_hook(14429077).delete()
        print ("Builder created!")


        bw.gcloud_config = GCloudConfig(instance=gcloud_instance, project=gcloud_project, zone=gcloud_zone, user=gcloud_user)

        OutputGenerator.init_project_output_folder(bw)


        bw.print_config()
        bws[repository_name] = bw

        print("repo hook: " + str(bw.project.hook))

        return 'Builder created with success'
    else:
        return "Builder already exists"

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return 'watched by mr4s'

@app.route('/outputs', defaults={'path': ''}, methods=['GET'])
@app.route('/outputs/<path:path>', methods=['GET'])
def get_output(path):
    print("Path:" + path)
    return send_from_directory('outputs', path)

def create_file_for_google_cloud_key(key_json, repository_name):
#    key_json = bytes(key_json, "utf-8").decode("unicode_escape")

    random_suffix = str(randint(0,100000000000000000000000))

    file_path = GCLOUD_PATH + "/" + repository_name + '-' + random_suffix + '.json'
    call(["mkdir", "-p", GCLOUD_PATH + "/" + repository_name])

    with open(file_path, "w") as f:
        json.dump(key_json, f)
#        f.write(key_json)

    call(["chmod", "400", file_path])

    return file_path

