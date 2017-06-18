import docker


class DockerImage:
    tag = None
    dependencies = None
    dockerfile = None

    def __init__(self, tag, dependencies, dockerfile):
        self.tag = tag
        self.dependencies = dependencies
        self.dockerfile = dockerfile

    @staticmethod
    def from_config(config):
        return DockerImage(tag=config["tag"], dependencies=config["dependencies"], dockerfile=config["dockerfile"])

    def print_config(self):
        print("tag: " + str(self.tag))
        print("dependencies: " + str(self.dependencies))
        print("dockerfile: " + str(self.dockerfile))


class StepResult:
    error = None
    namespace = None

    def __init__(self, error=None, namespace=None):
        self.error = error
        self.namespace = namespace

    def has_successed(self):
        return self.error == None

    def has_failed(self):
        return self.has_successed() == False

    def get_message(self):
        return "No output"

    def get_error_msg(self):
        if self.error.__class__ is bytes:
            return self.error.decode("utf-8")
        else:
            return str(self.error)


class DockerBuildResult(StepResult):
    image = None

    def __init__(self, image, error, namespace=None):
        StepResult.__init__(self, error=error, namespace=namespace)
        self.image = image

    def get_message(self):
        return str(self.image)


class DockerRunResult(StepResult):
    stdout = None

    def __init__(self, stdout=None, error=None, namespace=None):
        StepResult.__init__(self, error=error, namespace=None)
        self.stdout = stdout


    def get_message(self):
        return str(self.stdout.decode("utf-8"))

class DockerAPI:
    client = None

    @staticmethod
    def init():
        DockerAPI.client = docker.from_env()

    @staticmethod
    def build(context_path,dockerfile, tag):
        try:
            print("Building image")
            print("context_path: " + context_path)
            print("dockerfile: " + dockerfile)
            print("tag: " + tag)

            image = DockerAPI.client.images.build(path=context_path, dockerfile=dockerfile,tag=tag)

            return DockerBuildResult(image=image, error=None)
        except docker.errors.BuildError as e:
            return DockerBuildResult(image=None, error=e.stderr)

    @staticmethod
    def run(image):
        try:
            result = DockerAPI.client.containers.run(image, stdout=True)
            return DockerRunResult(stdout=result)
        except (docker.errors.ContainerError) as e:
            return DockerRunResult(error=e.stderr)
        except (docker.errors.ImageNotFound, docker.errors.APIError) as e:
            return DockerRunResult(error=e)

    @staticmethod
    def push(docker_image, dhub_u, dhub_p):
        print("Pushing image with tag: " + docker_image.tag)
        print("dhub_u: " + dhub_u)
        print("dhub_p: " + dhub_p)

        if (dhub_u is not None and dhub_p is not None):
            DockerAPI.client.images.push(repository=docker_image.tag, auth_config={"username": dhub_u, "password": dhub_p})
        else:
            DockerAPI.client.images.push(repository=docker_image.tag)

    @staticmethod
    def erase(image):
        try:
            DockerAPI.client.images.remove(image=image, force=True)
        except docker.errors.ImageNotFound as e:
            pass

    @staticmethod
    def foo():
        print(str(type(DockerAPI.client)))


#DockerAPI.init()
#DockerAPI.foo()
#result = DockerAPI.build(dockerfile="SampleDockerFile", tag="sample", context_path=".")
#print(result.image)
#print(result.error)

#result = DockerAPI.run('sample')
#print("stdout => " + str(result.stdout))
#print("error => " + str(result.error))
