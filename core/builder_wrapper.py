from github import Github
import yaml
import base64


class Project:
    gwrap = ""
    repo = ""
    branch = ""
    last_commit = ""

    def __init__(self):
        pass

    def load(self, git_api_key, repository_name):
        self.gwrap = Github(git_api_key)
        self.repo = self.gwrap.get_repo(repository_name)
        self.branch = self.repo.get_branch(self.repo.default_branch)
        self.last_commit = self.branch.commit

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


    build_steps = []
    output_dir = ""


    test_dependent_images = []
    test_steps = []

    run_steps = []

    def __init__(self, git_api_key, docker_hub_key, google_cloud_key, repository_name):
        self.secret_keys = SecretKeys(git_api_key, docker_hub_key, google_cloud_key)
        self.project = Project()
        self.ua_config = UaConfig()
        self.project.load(git_api_key, repository_name)
        self.load_benga_conf()

    def load_benga_conf(self):
        # content = base64.b64decode(self.project.repo.get_file_contents('benga.yml').content)
        content = ""

        with open('/home/mras/cloud/benga.yml') as myfile:
            content = myfile.read()

        config = yaml.load(content)

        self.build_steps = config["build"]["steps"]
        self.output_dir = config["build"]["output_dir"]

        self.test_steps = config["test"]["run_steps"]
        self.test_dependent_images = config["test"]["dependent_images"]

        self.ua_config.project_language = config["user_acceptance"]["project_language"]
        self.ua_config.min_coverage = config["user_acceptance"]["min_coverage"]

        self.run_steps = config["production"]["run_steps"]

    def is_outdate(self):
        curr_commit = self.repo.commit
        return curr_commit != last_commit

    def print_config(self):
        print ("build_steps: " + str(self.build_steps))
        print ("output_dirs: " + str(self.output_dir))
        print ("test_steps: " + str(self.test_steps))
        print ("test_dependent_images: " + str(self.test_dependent_images))
        print ("ua_config.prroject_language:: " + str(self.ua_config.project_language))
        print ("ua_config.min_coverage: " + str(self.ua_config.min_coverage))
        print ("run_steps: " + str(self.run_steps))

    def get_output_dir(self):
        return self.path + "/" + self.output_dir

# g = Github("966123f71b2bd6dce2d242f96b4ab5d0ceedfc7d")
# b = BuilderWrapper(git_api_key="966123f71b2bd6dce2d242f96b4ab5d0ceedfc7d", repository_name="marlonwc3/cloud-example", docker_hub_key="", google_cloud_key="")
# b.path = "."


# repo = b.project.repo
# branch = b.project.branch

# b.print_config()

