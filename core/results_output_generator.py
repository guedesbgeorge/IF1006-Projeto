from subprocess import call


MARKUP_BEGIN = "<!DOCTYPE html><html><head><style>table{font-family: arial, sans-serif; border-collapse: collapse; width: 100%;}tr{background-color: gray;}td, th{border: 1px solid #dddddd;text-align: left;padding: 8px;}.success{background-color: green;}.failed{background-color: red;}</style></head><body>"

MARKUP_END = "</body></html>"

TABLE_BEGIN = "<table> <tr> <th>Step</th> <th>Result</th> <th>Output</th> </tr>"
TABLE_END = "</table>"

SUCCESSED_TR = "<tr class=\"success\">"
FAILED_TR  = "<tr class=\"failed\">"

LOADING_MESSAGE = "<h4>Building project . . . this can take a few minutes</h4>"


OUTPUT_FOLDER = "outputs"


class OutputGenerator:
    @staticmethod
    def save_markup(bw, markup):
        with open(OUTPUT_FOLDER+"/"+bw.project.repository_name+"/build_"+str(bw.count)+".html", "w") as f:
            f.write(markup)

    @staticmethod
    def init_project_output_folder(bw):
        call(["mkdir", "-p", OUTPUT_FOLDER+"/"+bw.project.repository_name])

    def init_outputs_folder():
        call(["mkdir", "-p", OUTPUT_FOLDER])

    @staticmethod
    def create_result_markup(bw, results):
        markup = MARKUP_BEGIN
        markup += OutputGenerator.generate_project_header(bw)
        try:
            markup += OutputGenerator.generate_project_details(bw)
        except Exception as e:
            pass

        markup += OutputGenerator.generate_step_table(bw, results)
        markup += MARKUP_END

        OutputGenerator.save_markup(bw, markup)

    @staticmethod
    def generate_loading_markup(bw):
        markup = MARKUP_BEGIN
        markup += OutputGenerator.generate_project_header(bw)
        markup += LOADING_MESSAGE
        markup += MARKUP_END

        OutputGenerator.save_markup(bw, markup)

    @staticmethod
    def generate_project_header(bw):
        return "<h3>" + bw.project.repository_name + "</h3>"

    @staticmethod
    def generate_project_details(bw):
        content = "<h5>commit: " + str(bw.get_current_commit()) + "</h5>"
        content += "<h5>dockerhub production tag: " + bw.prod_image.tag + "</h5>"
        content += "<h5>dockerhub test tag: " + bw.test_image.tag + "</h5>"
        content += "<h5>google cloud project: " + bw.gcloud_config.project + "</h5>"
        content += "<h5>google cloud instance: " + bw.gcloud_config.instance + "</h5>"

        return content

    @staticmethod
    def generate_step_table(bw, results):
        content = TABLE_BEGIN
        for result in results:
            content += OutputGenerator.get_result_tr(result)
            content += "<td>" + result.namespace + "</td>"
            content += "<td>" + OutputGenerator.get_result_state(result) + "</td>"
            content += "<td>" + OutputGenerator.get_result_message(result) + "</td>"
            content += "</tr>"
        content += TABLE_END

        return content


    @staticmethod
    def get_result_state(result):
        if result.has_failed():
            return "FAILED"
        return "SUCCESSED"

    @staticmethod
    def get_result_message(result):
        if result.has_failed():
            return result.get_error_msg()
        return result.get_message()

    @staticmethod
    def get_result_tr(result):
        if result.has_failed():
            return FAILED_TR
        return SUCCESSED_TR
