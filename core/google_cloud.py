from subprocess import call


class GCloudAPI:
    @staticmethod
    def activate_service(gcloud_config):
        print("RUNNING: " + " ".join(["gcloud", "auth", "activate-service-account", "--key-file", gcloud_config.key_file]))
        call(["gcloud", "auth", "activate-service-account", "--key-file", gcloud_config.key_file])
#        print("COMMAND:")
#        print(" ".join(["echo", "", "|", "gcloud", "compute", "--project", gcloud_config.project, "ssh", "--zone",  gcloud_config.zone, gcloud_config.instance, "--            command", "ps"]))
        call(["echo", "", "|", "gcloud", "compute", "--project", gcloud_config.project, "ssh", "--zone",  gcloud_config.zone, gcloud_config.instance, "--command", "ps"])


    @staticmethod
    def run_command(gcloud_config, commands_str):
        print("COMMANDS: " + str(commands_str))
        prefix_commands = ["gcloud", "compute", "--project", gcloud_config.project,"ssh",  "--zone", gcloud_config.zone, gcloud_config.instance, "--command"]

        prefix_commands.append(" ".join(commands_str))
        commands = prefix_commands

        print("Exec commands: " + str(commands))

        call(commands)
