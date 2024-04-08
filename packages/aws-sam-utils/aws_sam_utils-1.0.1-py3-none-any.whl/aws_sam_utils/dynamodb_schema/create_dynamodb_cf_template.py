import sys
import os
import yaml
from .shared import *

def create_aws_resources(stack_name, tables_dict, throughput):
    resources = {
        "Resources": {
        }
    }

    for key, value in tables_dict.items():
        table_name = key
        full_table_name = stack_name+'-'+key
        table_config = value

        resources["Resources"][table_name] = get_aws_resource(full_table_name, table_config, throughput)

    resources_yaml = yaml.safe_dump(resources, indent=4).replace("Resources:", "")
    return resources_yaml

def main():
    schema_file = sys.argv[1]
    output_file = sys.argv[2]
    stack_name = os.environ["STACK_NAME"]

    schema = read_yaml(schema_file)
    resources_yaml = create_aws_resources(stack_name, schema["Tables"], schema['ProvisionedThroughput'])

    with open(output_file, "w") as f:
        f.write(resources_yaml)

if __name__ == "__main__":
    main()