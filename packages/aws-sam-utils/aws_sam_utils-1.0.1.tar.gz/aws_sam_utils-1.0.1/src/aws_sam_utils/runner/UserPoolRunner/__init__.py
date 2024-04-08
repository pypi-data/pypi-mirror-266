from ..TemplateRunner import TemplateRunner

class UserPoolRunner(TemplateRunner):
    def __init__(self, args, config):
        super().__init__(args, config)
        print(f"""Command:
{args.command}

UserPool Parameters:
DOMAIN_NAME={config["DOMAIN_NAME"]}
AUTH_SUBDOMAIN={config["AUTH_SUBDOMAIN"]}
""")
        if not config["DOMAIN_NAME"] or not config["AUTH_SUBDOMAIN"]:
            raise Exception("check DOMAIN_NAME & AUTH_SUBDOMAIN in .env")

    def setup(self):
        self.run_cmd("sam build")
        self.run_cmd(f"sam deploy --stack-name {self.stack} --parameter-overrides DomainName={self.config['DOMAIN_NAME']} AuthSubdomain={self.config['AUTH_SUBDOMAIN']}")

    def teardown(self):
        self.run_cmd(f"sam delete --no-prompts --stack-name {self.stack}")
