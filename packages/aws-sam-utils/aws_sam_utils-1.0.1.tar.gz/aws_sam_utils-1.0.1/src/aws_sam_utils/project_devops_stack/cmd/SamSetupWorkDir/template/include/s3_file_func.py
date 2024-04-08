                    import boto3
                    import botocore
                    import json
                    import os
                    import traceback
                    import cfnresponse
                    import zipfile
                    import textwrap

                    s3 = boto3.resource("s3", region_name=os.environ["AWS_REGION"])
                    cfn = boto3.client("cloudformation", region_name=os.environ["AWS_REGION"])

                    def handler(event, context):
                        print(json.dumps(event))
                        try:
                            phys_id = event.get("PhysicalResourceId")
                            logical_id = event["LogicalResourceId"]
                            stack_id = event["StackId"]
                            rp = event["ResourceProperties"]
                            s3_obj = s3.Object(os.environ['S3_BUCKET'], os.environ['S3_KEY'])
                            if event["RequestType"] in ["Create", "Update"]:
                                # Build the initial CodeCommit repository as a zip file
                                local_zip = '/tmp/initial-repository-code.zip'
                                zf = zipfile.ZipFile(local_zip, mode='w', compression=zipfile.ZIP_DEFLATED)
                                zf.writestr('README.md', textwrap.dedent(f"""\
                                # {{ repo }}
                                """))
                                zf.close()
                                # Store the zip file in S3 to be loaded into the CodeCommit initial repository
                                s3_obj.put(Body=open(local_zip, 'rb'))
                            elif event["RequestType"] == "Delete":
                                s3_obj.delete()
                            
                            cfnresponse.send(
                                event,
                                context,
                                cfnresponse.SUCCESS,
                                {'Bucket': os.environ['S3_BUCKET'], 'Key': os.environ['S3_KEY']},
                                physicalResourceId=phys_id,
                            )
                        except Exception as e:
                            print(f"Error - {repr(e)} - {traceback.format_exc()}")
                            cfnresponse.send(event, context, cfnresponse.FAILED, {}, physicalResourceId=phys_id, reason=repr(e))
