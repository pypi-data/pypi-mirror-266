import os
import tempfile
import pkg_resources
from termcolor import colored
import subprocess
from pathlib import Path
import shutil

class WorkDir:
    def __init__(self, project, repo):
        self.project = project
        self.repo = repo
        self.stack_name = f"{project}-{repo}"

    def run(self, commands):
        with tempfile.TemporaryDirectory(delete=True) as self.work_dir:
            print(colored(f'work directory: {self.work_dir}', 'green'))
            self.prepare_work_dir_files()
            for command in commands:
                self.run_cmd(command)

    def prepare_work_dir_files(self):
        config_file_path = pkg_resources.resource_filename(__name__, 'samconfig.toml')
        with open(config_file_path, 'r') as file:
            data = file.read()
            data = data.replace("$STACK_NAME", self.stack_name)
            data = data.replace("$S3_PREFIX", self.stack_name.lower())
            with open(os.path.join(self.work_dir, "samconfig.toml"), 'w') as destConf:
                destConf.write(data)
        
        self.generate_template_file_resources()

    def generate_template_file_resources(self):
        raise Exception("this method should be overrided")
    
    def run_cmd(self, cmd):
        print(colored(cmd, 'green'))
        process = subprocess.run(f"cd {self.work_dir} && {cmd}", shell=True, capture_output=True, text=True)
        print(colored(process.stdout, 'light_grey'))
        print(colored(process.stderr, 'red'))
