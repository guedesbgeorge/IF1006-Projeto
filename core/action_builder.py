from builder_wrapper import BuilderWrapper
from docker_api import DockerAPI
from docker_api import DockerImage
from docker_api import StepResult



LOAD_BENGA_CONF = (lambda bw: ActionBuilder.load_benga_conf(bw), 'LOAD_BENGA_CONF')
CLONE_REPO = (lambda bw: ActionBuilder.clone_repo(bw), 'CLONE_REPO')
BUILD_TEST_IMAGE = (lambda bw: ActionBuilder.build_test_image(bw), 'BUILD_TEST_IMAGE')
RUN_TESTS = (lambda bw: ActionBuilder.run_tests(bw), 'RUN_TESTS')
PUSH_TEST_IMAGE = (lambda bw: ActionBuilder.push_test_image(bw), 'PUSH_TEST_IMAGE')


pipeline = [LOAD_BENGA_CONF, CLONE_REPO, BUILD_TEST_IMAGE, RUN_TESTS, PUSH_TEST_IMAGE]

class ActionBuilder:

    @staticmethod
    def start_pipeline(bw):
        try:
            results = []
            last_result = None

            for step in pipeline:
                result = ActionBuilder.run_step(bw=bw, step=step[0], namespace=step[1],last_result=last_result)
                results.append(result)
                last_result = result

            return list(filter(lambda result: result is not None, results))

        except Exception as e:
            raise e
        finally:
            DockerAPI.erase(bw.test_image.tag)



    @staticmethod
    def run_step(bw, step, namespace, last_result=None):
        if (last_result is not None and last_result.has_failed()):
            return None

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
            return StepResult()
        except Exception as e:
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

    def push_test_image(bw):
        DockerAPI.push(bw.test_image, dhub_u=bw.secrets.docker_hub_u, dhub_p=bw.secrets.docker_hub_p)
        return StepResult()

    def get_context_path(bw):
        return bw.project.repository_name+"/."
