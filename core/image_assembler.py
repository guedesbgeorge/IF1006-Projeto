from builder_wrapper import BuilderWrapper

class ImageAssembler:

    def __init__(self):
        pass

    @staticmethod
    def assemble_production_image(builder_wrapper, base_image, output_dir):
        with open('{0}/ProductionImage'.format(output_dir),'w+') as f:
                f.write(base_image)
                f.write("RUN mkdir bin\n")
                f.write("COPY {0}/* ./bin".format(builder_wrapper.get_output_dir()) + "\n")
                f.write(" && ".join(builder_wrapper.run_steps)+"\n")


b = BuilderWrapper(git_api_key="966123f71b2bd6dce2d242f96b4ab5d0ceedfc7d", repository_name="marlonwc3/cloud-example",      docker_hub_key="", google_cloud_key="")
b.path = "."
b.print_config()
print(b.get_output_dir())

image = "."

with open('Dockerfile', 'r') as myfile:
        image=myfile.read()


ImageAssembler.assemble_production_image(b, image, '..')

