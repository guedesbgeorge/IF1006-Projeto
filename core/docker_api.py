import docker


class DockerBuildResult:
    image = None
    error = None

    def __init__(self, image, error):
        self.image = image
        self.error = error

    def has_successed(self):
        return self.error == None

    def has_failed(self):
        return self.has_success() == False

class DockerRunResult:
    error = None
    stdout = None

    def __init__(self, stdout=None, error=None):
        self.error = error
        self.stdout = stdout

    def has_successed(self):
        return self.error == None

    def has_failed(self):
        return self.has_success() == False


class DockerAPI:
    client = None

    @staticmethod
    def init():
        DockerAPI.client = docker.from_env()

    @staticmethod
    def build(context_path,filename, tag):
        try:
            image = DockerAPI.client.images.build(path=context_path, dockerfile=filename,tag=tag)
            return DockerBuildResult(image=image, error=None)
        except (docker.errors.APIError, docker.errors.BuildError) as e:
            return DockerBuildResult(image=None, error=e)

    @staticmethod
    def run(image):
        try:
            result = DockerAPI.client.containers.run(image, stdout=True)
            return DockerRunResult(stdout=result)
        except (docker.errors.ContainerError, docker.errors.ImageNotFound, docker.errors.APIError) as e:
            return DockerRunResult(error=e)


    @staticmethod
    def foo():
        print(str(type(DockerAPI.client)))


DockerAPI.init()
DockerAPI.foo()
result = DockerAPI.build(filename="SampleDockerFile", tag="sample", context_path=".")
print(result.image)
print(result.error)

result = DockerAPI.run('sample')
print("stdout => " + str(result.stdout))
print("error => " + str(result.error))
