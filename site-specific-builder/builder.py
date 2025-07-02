import re
import json
import os

HEADER_BASE = './header_base.html'
FOOTER_BASE = './footer_base.html'
# Sometimes the file needs some tags at the top to balance out what it contains so the formatter can make it look pretty.
BEGIN_KEY = '#begin'
ALL = 'a';

def get_replacement(page_layout: str, data: dict, key: str):
    if key == "header_mb-4":
        # check if true or false. If true, return "mb-4", which will place a margin below
        if data[key]:
            return " mb-4"
        else:
            return ""

    elif key == "header_content" or key == "footer_content":
        # fetch file content from header_content or footer_content file name. will have to start fetching from below the #begin line
        content = ""
        file_start = False

        with open(data[key], 'r') as f:
            file_start = False
            content = ""
            for line in f:
                if BEGIN_KEY in line:
                    file_start = True
                elif file_start:
                    content += line

        f.close()
        return content

    else:
        raise ExceptionType("Unrecognizable key")


def render_line(page_layout, data, line, context):
    matches = re.findall(r"{{\s*(.*?)\s*}}", line)
    modifiedLine = line
    for m in matches:
        replacement = get_replacement(page_layout, data, m)
        modifiedLine = re.sub(r"\s*{{" + m + r"}}", replacement, line)

    return modifiedLine;



def build_file(page_layout: str):
    json_config = './' + page_layout + '/config.json'

    output_dir = f'build/{page_layout}'
    os.makedirs(output_dir, exist_ok=True)  # create dir if it doesn't exist

    header_output = os.path.join(output_dir, 'header.html')
    footer_output = os.path.join(output_dir, 'footer.html')

    with open(json_config, 'r') as f:
        data = json.load(f)

    with open(HEADER_BASE, 'r') as header_in, open(header_output, 'w') as header_out:
        file_start = False
        for line in header_in:
            if BEGIN_KEY in line:
                file_start = True
            elif file_start:
                rendered = render_line(page_layout, data, line, data)
                header_out.write(rendered)

    with open(FOOTER_BASE, 'r') as footer_in, open(footer_output, 'w') as footer_out:
        file_start = False
        for line in footer_in:
            if BEGIN_KEY in line:
                file_start = True
            elif file_start:
                rendered = render_line(page_layout, data, line, data)
                footer_out.write(rendered)

build_options = {
    "Site Specific": "site-specific",
    "Site Specific: Full Width": "site-specific-full-width"
}

print("Which file to build?")

options_list = list(build_options.keys())

for i, b in enumerate(options_list):
    print(i, "-", b)

print(ALL,  "- All files")
selection = input("Pick page layout: ")  # input() takes one argument: the prompt

if (selection == ALL):
    for option in build_options:
        selected_value = build_options[option]

        print("Building", selected_value)

        build_file(selected_value)

    print("Finished generating all files.")

else:
    selected_key = options_list[int(selection)]
    selected_value = build_options[selected_key]
    print("Building ", selected_value)

    build_file(selected_value)

    print("Finished generating ", selected_value, " files.")

