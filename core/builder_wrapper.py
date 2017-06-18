from github import Github
import yaml
import base64
import os
from subprocess import call
from docker_api import DockerImage

from random import randint

class GCloudConfig:
    def __init__(self, project, instance, zone, key_file=None):
        self.key_file = key_file
        self.project = project
        self.instance = instance
        self.zone = zone

class Project:
    gwrap = ""
    repo = ""
    last_commit = ""
    hook = ""
    hook_id = ""
    repository_name = ""

    def __init__(self):
        pass

    def load(self, git_api_key, repository_name, hook_id):
        self.gwrap = Github(git_api_key)
        self.repository_name = repository_name
        self.repo = self.gwrap.get_repo(repository_name)
        self.hook = None
        self.hook_id = hook_id
        self.gcloud_config = None

        if self.hook_id == None:
            self.get_repo_hook()
        else:
            print("Hook already created with id="+str(hook_id))

    def get_branch(self):
        return self.repo.get_branch(self.repo.default_branch)

    def get_repo_hook(self):
        print("Creating hook")
        if (self.hook_id == None):
            self.hook = self.repo.create_hook(name="web", config={"url": os.environ['WEB_HOOK_ROUTE'], "content_type": "json"})
            # self.hook = self.repo.create_hook(name="web", config={"url": "127.0.0." + str(randint(3,255)), "content_type": "json"})
            self.hook_id = self.hook.id
            print("Hook well created with id="+str(self.hook_id))
        return self.hook

class SecretKeys:
    git_api_key = ""

    docker_hub_u = ""
    docker_hub_p = ""

    def __init__(self, git_api_key, docker_hub_u, docker_hub_p):
        self.git_api_key = git_api_key
        self.docker_hub_u = docker_hub_u
        self.docker_hub_p = docker_hub_p

class UaConfig:
    project_language = ""
    min_coverage = ""

    def __init__(self):
        pass

class BuilderWrapper:
    """Wrap a state of a builder"""
    path = ""

    project = ""
    secrets = ""
    ua_config = ""

    pro_image = None
    test_image = None

    def __init__(self, git_api_key, docker_hub_u, docker_hub_p,repository_name, hook_id):
        self.secrets = SecretKeys(git_api_key, docker_hub_u, docker_hub_p)
        self.project = Project()
        self.project.load(git_api_key, repository_name, hook_id)
        self.ua_config = UaConfig()
        self.prod_image = None
        self.test_image = None

    def load_benga_conf(self):
        content = base64.b64decode(self.project.repo.get_file_contents('benga.yml').content)
        # content = ""

        # with open('/home/mras/cloud/benga.yml') as myfile:
        #    content = myfile.read()

        config = yaml.load(content)

        self.ua_config.project_language = config["user_acceptance"]["project_language"]
        self.ua_config.min_coverage = config["user_acceptance"]["min_coverage"]


        self.prod_image = DockerImage.from_config(config["production"])
        self.test_image = DockerImage.from_config(config["test"])

    def is_outdate(self, commit):
        return (self.project.get_branch().commit == commit) is False

    def clone_repo(self):
        clone_url = self.get_clone_url()

        name = self.project.repo.name
        name_len = name.__len__()
        name_prefix_ws = self.project.repository_name[:-name_len]

        call(["rm", "-rf", name_prefix_ws])
        call(["git", "clone", str(clone_url)])
        call(["mkdir", "-p", name_prefix_ws])
        call(["mv",  name, name_prefix_ws])

    def erase_repo(self):
        call(["rm", "-rf", self.project.repository_name])

    def get_clone_url(self):
        url = self.project.repo.clone_url
        if (url.startswith("https://")):
                return url[:8] + self.secrets.git_api_key + "@" + url[8:]
        elif (urls.startswith("http://")):
                return url[:7] + self.secrets.git_api_key + "@" + url[7:]
        else:
            raise Exception('unknown clone url: ' + url)



    def print_config(self):
        print ("ua_config.prroject_language: " + str(self.ua_config.project_language))
        print ("ua_config.min_coverage: " + str(self.ua_config.min_coverage))
        if self.prod_image is not None and self.test_image is not None:
            self.prod_image.print_config()
            self.test_image.print_config()
      # g = Github("966123f71b2bd6dce2d242f96b4ab5d0ceedfc7d")
# b = BuilderWrapper(git_api_key="3fea2d8fd7690176b4ff9d69a61e49435f164cdf", repository_name="marlonwc3/cloud-example", docker_hub_key="", google_cloud_key="")
# b.path = "."


# repo = b.project.repo
# branch = b.project.branch

# b.print_config()

