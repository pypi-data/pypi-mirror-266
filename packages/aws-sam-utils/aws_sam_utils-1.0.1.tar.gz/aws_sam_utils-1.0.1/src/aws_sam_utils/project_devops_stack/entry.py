import sys
import os
import yaml
from .cmd.SamSetupWorkDir import SamSetupWorkDir
from .cmd.SamTearDownWorkDir import SamTearDownWorkDir

def main():
    type = sys.argv[1]
    assert(type in ["setup", "teardown"])
    project = sys.argv[2]
    repo = sys.argv[3]
    assert(project and repo)

    if type == 'setup':
        SamSetupWorkDir(project, repo).setup()
    else:
        SamTearDownWorkDir(project, repo).teardown()
