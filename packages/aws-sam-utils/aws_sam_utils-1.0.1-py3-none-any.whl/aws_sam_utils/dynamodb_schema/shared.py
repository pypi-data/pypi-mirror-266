import yaml

def read_yaml(file_path):
    with open(file_path) as stream:
        template = yaml.safe_load(stream)
        return template

def get_aws_resource(full_table_name, table_config, throughput):
    resource = {
        "Type": 'AWS::DynamoDB::Table',
        "Properties":{
            "TableName": full_table_name,
            "AttributeDefinitions": [{
                "AttributeName": "id",
                "AttributeType": "S"
            }],
            "KeySchema":[{
                "AttributeName": "id",
                "KeyType": "HASH"
            }],
            "ProvisionedThroughput":{
                "ReadCapacityUnits": throughput["ReadCapacityUnits"],
                "WriteCapacityUnits": throughput["WriteCapacityUnits"]
            }
        }
    }
    if not table_config:
        return resource
    
    if "UniqueFields" in table_config:
        if not "GlobalSecondaryIndexes" in table_config:
            resource["Properties"]["GlobalSecondaryIndexes"] = []
        for uf in table_config["UniqueFields"]:
            resource["Properties"]["AttributeDefinitions"].append(uf)
            uf_index = {
                "IndexName": f"{full_table_name}-UkIndex-{uf["AttributeName"]}",
                "KeySchema": [{ 
                    "AttributeName": uf["AttributeName"],
                    "KeyType": "HASH" }],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": throughput["ReadCapacityUnits"],
                    "WriteCapacityUnits": throughput["WriteCapacityUnits"]
                }
            }
            resource["Properties"]["GlobalSecondaryIndexes"].append(uf_index)
    if "ForeignTables" in table_config:
        if not "GlobalSecondaryIndexes" in resource["Properties"]:
            resource["Properties"]["GlobalSecondaryIndexes"] = []
        for ft in table_config["ForeignTables"]:
            ft_attr = { "AttributeName": f"id{ft}", "AttributeType": "S" }
            ft_index = {
                "IndexName": f"{full_table_name}-FkIndex-id{ft}",
                "KeySchema": [
                    { "AttributeName": f"id{ft}", "KeyType": "HASH" },
                    { "AttributeName": "id", "KeyType": "RANGE" }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": throughput["ReadCapacityUnits"],
                    "WriteCapacityUnits": throughput["WriteCapacityUnits"]
                }
            }
            resource["Properties"]["AttributeDefinitions"].append(ft_attr)
            resource["Properties"]["GlobalSecondaryIndexes"].append(ft_index)

    if "TimeToLiveField" in table_config:
        resource["Properties"]["TimeToLiveSpecification"] = {
            "AttributeName": table_config["TimeToLiveField"],
            "Enabled": True
        }

    return resource
