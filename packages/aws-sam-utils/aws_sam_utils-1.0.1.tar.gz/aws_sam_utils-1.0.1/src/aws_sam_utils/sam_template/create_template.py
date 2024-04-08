import os
import sys
import re
from io import StringIO
from pathlib import Path
from dotenv import dotenv_values
from jinja2 import Environment, FileSystemLoader

def main():
    template_file = sys.argv[1]
    data_file = sys.argv[2]

    data = dotenv_values(data_file)
    data["lambdas"] = get_backend_lambda_configs()
    env =  Environment(loader=FileSystemLoader("."), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_file)

    output = template.render(data)
    print(output)

def get_backend_lambda_configs():
    backend_root_dir = os.environ["BACKEND_ROOT_DIR"]
    entry_path = os.path.join(backend_root_dir,"src","main","entry","api")
    entry_files = Path(entry_path).glob(os.path.join("**","*"))

    lambdas = []
    for entry_file in list(entry_files):
        lambdas.extend(parse_lambdas_from_entry_file(entry_file))
    return lambdas

def parse_lambdas_from_entry_file(entry_file):
    lines = None
    with open(entry_file, "r", encoding='utf-8') as f:
        lines = f.readlines()

    file_name = Path(entry_file).stem
    file_lambdas = []

    for i, line in enumerate(lines):
        match = re.search(r'(?<=export const ).*(?= \= async \()', line)
        if match:
            handler_name = match.group(0)
            comment = parse_lambda_comment(lines, i)
            path = comment["path"] if "path" in comment else f"/{file_name}/{handler_name}"

            file_lambdas.append({
                'name': file_name[0].upper() + file_name[1:] + handler_name[0].upper() + handler_name[1:],
                'file_name': file_name,
                'handler_name': handler_name,
                'path': path,
                'method': comment["method"] if "method" in comment else "post"
            })
    
    return file_lambdas

def parse_lambda_comment(lines, index):
    # find comment lines backward from the index line
    # parse the commented content to dict
    comment_lines = []
    for i in reversed(range(0,index)):
        if lines[i].startswith('//'):
            comment_lines.append(lines[i][2:])
        else:
            break
    if(len(comment_lines)>0):
        config = '\n'.join(comment_lines)
        return dotenv_values(stream=StringIO(config))
    else:
        return {}

if __name__ == "__main__":
    main()
