from subprocess import call


class GCloudAPI:
    @staticmethod
    def activate_service(gcloud_config):
        print("RUNNING: " + " ".join(["gcloud", "auth", "activate-service-account", "--key-file", gcloud_config.key_file]))
        call(["gcloud", "auth", "activate-service-account", "--key-file", gcloud_config.key_file])
#        print("COMMAND:")
#        print(" ".join(["echo", "", "|", "gcloud", "compute", "--project", gcloud_config.project, "ssh", "--zone",  gcloud_config.zone, gcloud_config.instance, "--            command", "ps"]))
        call(["gcloud", "compute", "--project", gcloud_config.project, "ssh", "--quiet", "--zone",  gcloud_config.zone, GCloudAPI.instance_with_user(gcloud_config), "--command", "ps"])


    @staticmethod
    def run_command(gcloud_config, commands_str):
        print("COMMANDS: " + str(commands_str))
        prefix_commands = ["gcloud", "compute", "--project", gcloud_config.project,"ssh", "--quiet", "--zone", gcloud_config.zone, GCloudAPI.instance_with_user(gcloud_config), "--command"]

        prefix_commands.append(" ".join(commands_str))
        commands = prefix_commands

        print("Exec commands: " + str(commands))

        call(commands)

    @staticmethod
    def instance_with_user(gcloud_config):
        return gcloud_config.user + '@' + gcloud_config.instance
