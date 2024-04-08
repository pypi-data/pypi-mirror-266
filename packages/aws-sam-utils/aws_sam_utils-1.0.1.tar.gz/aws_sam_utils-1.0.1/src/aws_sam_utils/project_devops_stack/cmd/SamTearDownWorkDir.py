from ..WorkDir import WorkDir

class SamTearDownWorkDir(WorkDir):
    def __init__(self, project, repo):
        super().__init__(project, repo)

    # create sam template file: template.yaml and resources under self.work_dir
    def generate_template_file_resources(self):
        print("nothing to do in teardown operation")

    def teardown(self):
        commands = [
            f"sam delete --no-prompts --stack-name {self.stack_name}"
        ]
        self.run(commands)
