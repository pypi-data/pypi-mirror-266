#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""comment here"""
import argparse
from dotenv import dotenv_values
import boto3
import sys
from importlib.metadata import version
from termcolor import colored

from .runner import *


def aws_sam_template():
    parser = argparse.ArgumentParser(description='create/delete AWS Cloudformation Stack.', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('template', type=str, help='template')
    parser.add_argument('command', type=str, help='setup or teardown')
    parser.add_argument('-v', '--version', action='version', version=version('aws_sam_utils'))
    args = parser.parse_args()

    config = dotenv_values("sam.config")

    if not args.template:
        raise Exception("no template is found.")
    
    klass = globals()[f'{args.template}Runner']
    runner = klass(args, config)
    runner.run()


def get_stack_output_value():
    stack = sys.argv[1]
    output_key = sys.argv[2]
    client = boto3.client('cloudformation')
    try:
        response = client.describe_stacks(StackName=stack)

        outputs = response["Stacks"][0]["Outputs"]
        for output in outputs:
                keyName = output["OutputKey"]
                if keyName == output_key:
                    print(output["OutputValue"])
                    return
    except:
         return