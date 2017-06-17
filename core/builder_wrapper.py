from github import Github
import yaml
import base64
import os

from random import randint

class Project:
    gwrap = ""
    repo = ""
    last_commit = ""
    hook = ""
    hook_id = ""

    def __init__(self):
        pass

    def load(self, git_api_key, repository_name, hook_id):
        self.gwrap = Github(git_api_key)
        self.repo = self.gwrap.get_repo(repository_name)
        self.hook = None
        self.hook_id = hook_id

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
    docker_hub_key = ""
    google_cloud_key = ""

    def __init__(self, git_api_key, docker_hub_key, google_cloud_key):
        self.git_api_key = git_api_key
        self.docker_hub_key = docker_hub_key
        self.google_cloud_key = google_cloud_key


class UaConfig:
    project_language = ""
    min_coverage = ""

    def __init__(self):
        pass

class BuilderWrapper:
    """Wrap a state of a builder"""
    path = ""

    project = ""
    secret_keys = ""
    ua_config = ""
    tag = ""

    build_steps = []
    output_dir = ""


    test_dependent_images = []
    test_steps = []

    run_steps = []

    def __init__(self, git_api_key, docker_hub_key, google_cloud_key, repository_name, hook_id):
        self.secret_keys = SecretKeys(git_api_key, docker_hub_key, google_cloud_key)
        self.project = Project()
        self.ua_config = UaConfig()
        self.project.load(git_api_key, repository_name, hook_id)
        self.load_benga_conf()

    def load_benga_conf(self):
        content = base64.b64decode(self.project.repo.get_file_contents('benga.yml').content)
        # content = ""

        # with open('/home/mras/cloud/benga.yml') as myfile:
        #    content = myfile.read()

        config = yaml.load(content)

        self.build_steps = config["build"]["steps"]
        self.output_dir = config["build"]["output_dir"]

        self.test_steps = config["test"]["run_steps"]
        self.test_dependent_images = config["test"]["dependent_images"]

        self.ua_config.project_language = config["user_acceptance"]["project_language"]
        self.ua_config.min_coverage = config["user_acceptance"]["min_coverage"]

        self.run_steps = config["production"]["run_steps"]

        #self.tag = config["tag"]


    def is_outdate(self, commit):
        return (self.project.get_branch().commit == commit) is False

    def print_config(self):
        print ("build_steps: " + str(self.build_steps))
        print ("output_dirs: " + str(self.output_dir))
        print ("test_steps: " + str(self.test_steps))
        print ("test_dependent_images: " + str(self.test_dependent_images))
        print ("ua_config.prroject_language:: " + str(self.ua_config.project_language))
        print ("ua_config.min_coverage: " + str(self.ua_config.min_coverage))
        print ("run_steps: " + str(self.run_steps))

    def get_output_dir(self):
        return "./" + self.output_dir

# g = Github("966123f71b2bd6dce2d242f96b4ab5d0ceedfc7d")
# b = BuilderWrapper(git_api_key="3fea2d8fd7690176b4ff9d69a61e49435f164cdf", repository_name="marlonwc3/cloud-example", docker_hub_key="", google_cloud_key="")
# b.path = "."


# repo = b.project.repo
# branch = b.project.branch

# b.print_config()

