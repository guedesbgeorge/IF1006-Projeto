from builder_wrapper import BuilderWrapper

class ImageAssembler:

    def __init__(self):
        pass

    @staticmethod
    def assemble_production_image(builder_wrapper, base_image, output_dir):
        with open('{0}/ProductionImage'.format(output_dir),'w+') as f:
                f.write(base_image)
                f.write("RUN mkdir build\n")
                f.write("COPY {0}/* build/".format(builder_wrapper.get_output_dir()) + "\n")
                f.write("WORKDIR build\n")
                ImageAssembler.write_cmd(builder_wrapper.run_steps, f)

    @staticmethod
    def assemble_test_image(builder_wrapper, base_image, output_dir):
        with open('{0}/TestImage'.format(output_dir),'w+') as f:
                f.write(base_image)
                f.write("RUN mkdir source\n")
                f.write("COPY {0}/* source/".format(builder_wrapper.path) + "\n")
                ImageAssembler.write_cmd(builder_wrapper.test_steps, f)

    @staticmethod
    def write_cmd(steps, f):
        f.write("CMD " + " && ".join(steps)+"\n")

# b = BuilderWrapper(git_api_key="7cf85aa94aa248b28431f2a87ffac19ffef9db4d", repository_name="marlonwc3/cloud-example",      docker_hub_key="", google_cloud_key="")
# b.path = "."
# b.print_config()
# print(b.get_output_dir())

# image = "."

# with open('Dockerfile', 'r') as myfile:
#        image=myfile.read()


# ImageAssembler.assemble_production_image(b, image, '..')

# ImageAssembler.assemble_test_image(b, image, '..')

