from builder_wrapper import BuilderWrapper
from docker_api import DockerAPI
from docker_api import DockerImage
from docker_api import StepResult
from google_cloud import GCloudAPI


LOAD_BENGA_CONF = (lambda bw: ActionBuilder.load_benga_conf(bw), 'LOAD_BENGA_CONF')

CLONE_REPO = (lambda bw: ActionBuilder.clone_repo(bw), 'CLONE_REPO')
BUILD_TEST_IMAGE = (lambda bw: ActionBuilder.build_test_image(bw), 'BUILD_TEST_IMAGE')
RUN_TESTS = (lambda bw: ActionBuilder.run_tests(bw), 'RUN_TESTS')
PUSH_TEST_IMAGE = (lambda bw: ActionBuilder.push_test_image(bw), 'PUSH_TEST_IMAGE')


BUILD_PROD_IMAGE = (lambda bw: ActionBuilder.build_prod_image(bw), 'BUILD_PROD_IMAGE')
PUSH_PROD_IMAGE = (lambda bw: ActionBuilder.push_prod_image(bw), 'PUSH_PROD_IMAGE')

DEPLOY_PROD_CONTAINER = (lambda bw: ActionBuilder.deploy_prod_container(bw), 'DEPLOY_PROD_CONTAINER')


pipeline = [LOAD_BENGA_CONF, CLONE_REPO, BUILD_TEST_IMAGE, RUN_TESTS, PUSH_TEST_IMAGE, BUILD_PROD_IMAGE, PUSH_PROD_IMAGE, DEPLOY_PROD_CONTAINER]

class ActionBuilder:

    @staticmethod
    def start_pipeline(bw):
        try:
            results = []
            last_result = None

            for step in pipeline:
                print ("Starting step: " + step[1])
                result = ActionBuilder.run_step(bw=bw, step=step[0], namespace=step[1],last_result=last_result)
                print ("Finishing step: " + step[1])
                results.append(result)
                last_result = result
                if result.has_failed():
                    print(str(result.get_error_msg()))
                    break

            return list(filter(lambda result: result is not None, results))

        except Exception as e:
            raise e
        finally:
            DockerAPI.erase(bw.test_image.tag)



    @staticmethod
    def run_step(bw, step, namespace, last_result=None):
        result = step(bw)
        result.namespace = namespace
        return result

    @staticmethod
    def load_benga_conf(bw):
        try:
            bw.load_benga_conf()
            return StepResult()
        except Exception as e:
            return StepResult(error="[Invalid Benga Conf]\n"+str(e))

    @staticmethod
    def clone_repo(bw):
        try:
            bw.clone_repo()
            bw.test_image.print_config()

            return StepResult()
        except Exception as e:
            print ("FUDEU CLONAR: " + str(e) )
            return StepResult(error=str(e))

    @staticmethod
    def build_test_image(bw):
        dockerfile = bw.test_image.dockerfile
        context = ActionBuilder.get_context_path(bw)
        tag = bw.test_image.tag

        return DockerAPI.build(dockerfile=dockerfile, tag=tag, context_path=context)

    @staticmethod
    def run_tests(bw):
        tag = bw.test_image.tag

        return DockerAPI.run(image=tag)

    @staticmethod
    def push_test_image(bw):
        DockerAPI.push(bw.test_image, dhub_u=bw.secrets.docker_hub_u, dhub_p=bw.secrets.docker_hub_p)
        return StepResult()

    @staticmethod
    def build_prod_image(bw):
        dockerfile = bw.prod_image.dockerfile
        context = ActionBuilder.get_context_path(bw)
        tag = bw.prod_image.tag

        return DockerAPI.build(dockerfile=dockerfile, tag=tag, context_path=context)

    @staticmethod
    def push_prod_image(bw):
        DockerAPI.push(bw.prod_image, dhub_u=bw.secrets.docker_hub_u, dhub_p=bw.secrets.docker_hub_p)
        return StepResult()

    @staticmethod
    def deploy_prod_container(bw):

        try:
            print ("Push image to deploy")
            GCloudAPI.run_command(bw.gcloud_config, ["sudo", "docker",  "login", "--password", bw.secrets.docker_hub_p, "--username", bw.secrets.docker_hub_u])
#            GCloudAPI.run_command(bw.gcloud_config, ["sudo", "docker",  "stop", "$(sudo docker ps -a -q)"])
#            GCloudAPI.run_command(bw.gcloud_config, ["sudo", "docker", "rm", "$(sudo docker ps -a -q)"])

            GCloudAPI.run_command(bw.gcloud_config, ["sudo", "docker", "pull", bw.prod_image.tag])

            exec_commands = ["sudo", "docker", "run"]
            if (bw.prod_image.run_args is not None):
                exec_commands += bw.prod_image.run_args.split(" ")

            exec_commands.append(bw.prod_image.tag)

            GCloudAPI.run_command(bw.gcloud_config, exec_commands)
            return StepResult()
        except Exception as e:
            return StepResult(error=str(e))


    def get_context_path(bw):
        return bw.project.repository_name+"/."

