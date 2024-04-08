import os
import tempfile
import pkg_resources
from termcolor import colored
import subprocess
from pathlib import Path
import shutil
import boto3

class TemplateRunner:
    def __init__(self, args, config):
        self.args = args
        self.config = config
        self.work_dir = None

        print(f"""Command:
{self.args.command}

Parameters:
STACK_NAME={self.config["STACK_NAME"]}
""")
        
        if not self.args.command:
            raise Exception(f"no command is found.")
        if not config["STACK_NAME"]:
            raise Exception("check STACK_NAME in .env")
        
        self.stack = config["STACK_NAME"]
        self.command = args.command

    def run(self):        
        with tempfile.TemporaryDirectory() as self.work_dir:
            print(colored(f'work directory: {self.work_dir}', 'green'))

            self.prepare_work_dir_files()

            cmd_func = getattr(self, self.command)
            cmd_func()

    def prepare_work_dir_files(self):
        config_file_path = pkg_resources.resource_filename(__name__, 'samconfig.toml')
        with open(config_file_path, 'r') as file:
            data = file.read()
            data = data.replace("$STACK_NAME", self.stack)
            data = data.replace("$S3_PREFIX", self.stack.lower())
            with open(os.path.join(self.work_dir, "samconfig.toml"), 'w') as destConf:
                destConf.write(data)
        
        template_dir = os.path.join(Path(config_file_path).parent, self.args.template + "Runner")
        shutil.copytree(template_dir, self.work_dir, dirs_exist_ok=True)
        # truncate __init__.py
        os.system(f"rm -rf {self.work_dir}/__init__.py && touch {self.work_dir}/__init__.py")

    def run_cmd(self, cmd):
        print(colored(cmd, 'green'))
        process = subprocess.run(f"cd {self.work_dir} && {cmd}", shell=True, capture_output=True, text=True)
        print(colored(process.stdout, 'light_grey'))
        print(colored(process.stderr, 'red'))

    def empty_s3_bucket(self, bucket):
        print(colored(f'Empty s3 bucket: {bucket}', 'yellow'))
        self.run_cmd(f"aws s3 rm s3://{bucket} --recursive")

    def empty_versioned_s3_bucket(self, bucket):
        s3 = boto3.resource('s3')
        try:
            bucket = s3.Bucket(bucket)
            bucket.object_versions.delete()
        except:
            return

    def empty_s3_buckets_in_stack(self, stack, buckets):
        client = boto3.client('cloudformation')
        try:
            response = client.describe_stacks(StackName=stack)
            outputs = response["Stacks"][0]["Outputs"]
            for output in outputs:
                    keyName = output["OutputKey"]
                    if keyName in buckets:
                        self.empty_s3_bucket(output["OutputValue"])
        except:
            return
        
    def setup(self):
        pass

    def teardown(self):
        pass
