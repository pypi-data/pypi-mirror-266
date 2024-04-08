import sys
import os
import json

from .shared import *

def create_json_file(json_file_path, full_table_name, table_config, throughput):
    resource = get_aws_resource(full_table_name, table_config, throughput)

    # DynamoDB local not support "TimeToLiveSpecification"
    if "TimeToLiveSpecification" in resource['Properties']:
        del resource['Properties']["TimeToLiveSpecification"]

    json_data = json.dumps(resource['Properties'], indent=4)
    with open(json_file_path, "w") as f:
        f.write(json_data)

def main():
    output_dir = sys.argv[2]
    schema_file = sys.argv[1]
    stack_name = os.environ["STACK_NAME"]

    schema = read_yaml(schema_file)

    for key, value in schema['Tables'].items():
        create_json_file(os.path.join(output_dir, key+'.json'), 
                         stack_name+'-'+key, 
                         value,
                         schema['ProvisionedThroughput'])

if __name__ == "__main__":
    main()