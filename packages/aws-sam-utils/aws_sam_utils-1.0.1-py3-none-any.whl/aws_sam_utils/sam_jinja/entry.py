import sys
from dotenv import dotenv_values
from jinja2 import Environment, FileSystemLoader

def main():
    template_file = sys.argv[1]
    data_file = sys.argv[2]

    data = dotenv_values(data_file)
    env =  Environment(loader=FileSystemLoader("."), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_file)

    output = template.render(data)
    print(output)

# if __name__ == "__main__":
#     main()
