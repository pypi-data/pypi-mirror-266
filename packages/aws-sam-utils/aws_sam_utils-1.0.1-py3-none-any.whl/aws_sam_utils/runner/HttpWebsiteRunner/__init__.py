import os
import shutil
from ..TemplateRunner import TemplateRunner

class HttpWebsiteRunner(TemplateRunner):
    def __init__(self, args, config):
        super().__init__(args, config)
        print(f"""Command:
{args.command}

HttpWebsite Parameters:
DOMAIN_NAME={config["DOMAIN_NAME"]}
WEBSITE_SUBDOMAIN={config["WEBSITE_SUBDOMAIN"]}
""")
        if not config["DOMAIN_NAME"] or not config["WEBSITE_SUBDOMAIN"]:
            raise Exception("check DOMAIN_NAME in .env")

    def setup(self):
        self.run_cmd("sam build")
        self.run_cmd(f"sam deploy --stack-name {self.stack} --parameter-overrides DomainName={self.config['DOMAIN_NAME']} WebsiteSubdomain={self.config['WEBSITE_SUBDOMAIN']}")

    def teardown(self):
        self.empty_s3_buckets_in_stack(self.stack, ["WebsiteBucket"])
        self.run_cmd(f"sam delete --no-prompts --stack-name {self.stack}")
