import os
import pkg_resources
from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader
from termcolor import colored
from ...WorkDir import WorkDir


class SamSetupWorkDir(WorkDir):
    def __init__(self, project, repo):
        super().__init__(project, repo)

    def generate_template_file_resources(self):
        print(f"create sam template file: template.yaml and resources under {self.work_dir}")
        index_file_path = pkg_resources.resource_filename(f"{__name__}.template", 'index.yaml')
        template_dir = Path(index_file_path).parent
        env =  Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template("index.yaml")
        output = template.render({
            "project": self.project,
            "repo": self.repo
        })

        template_file_path = os.path.join(self.work_dir, "template.yaml")
        with open(template_file_path, "w") as f:
            f.write(output)
        print(colored(f'create template file: {template_file_path}', 'green'))
        print(output)

    def setup(self):
        commands = [
            "sam build",
            f"sam deploy --stack-name {self.stack_name}"
        ]
        self.run(commands)