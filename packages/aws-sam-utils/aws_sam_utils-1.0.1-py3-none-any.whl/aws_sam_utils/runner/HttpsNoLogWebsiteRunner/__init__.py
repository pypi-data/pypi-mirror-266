import boto3

from ..TemplateRunner import TemplateRunner

class HttpsNoLogWebsiteRunner(TemplateRunner):
    def __init__(self, args, config):
        super().__init__(args, config)
        print(f"""Command:
{args.command}

Parameters:
DOMAIN_NAME={config["DOMAIN_NAME"]}
WEBSITE_SUBDOMAIN={config["WEBSITE_SUBDOMAIN"]}
CREATE_APEX={config["CREATE_APEX"]}
""")
        if not config["DOMAIN_NAME"] or not config["WEBSITE_SUBDOMAIN"]:
            raise Exception("check .env")
        
        # get route53 hosted zone id by domain name
        client = boto3.client('route53')
        resp = client.list_hosted_zones_by_name(DNSName=config["DOMAIN_NAME"])
        self.hosted_zone_id = resp['HostedZones'][0]['Id'].replace('/hostedzone/', '')
        if not self.hosted_zone_id:
            raise Exception("check domain name & route53 hosted zone.")

    def setup(self):
        self.run_cmd("sam build")
        self.run_cmd(f"sam deploy --stack-name {self.stack} --parameter-overrides DomainName={self.config['DOMAIN_NAME']} SubDomain={self.config['WEBSITE_SUBDOMAIN']} CreateApex={self.config['CREATE_APEX']} HostedZoneId={self.hosted_zone_id}")

    def teardown(self):
        self.empty_s3_buckets_in_stack(self.stack, ["S3BucketRoot"])
        # delete the stack
        self.run_cmd(f"sam delete --no-prompts --stack-name {self.stack}")
