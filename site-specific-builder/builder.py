import re
import json

HEADER_BASE = './header_base.html'
FOOTER_BASE = './footer_base.html'

HEADER_OUTPUT = './header_output.html'
FOOTER_OUTPUT = './footer_output.html'

JSON_CONFIG = './site-specific/ss.json'

# Sometimes the file needs some tags at the top to balance out what it contains so the formatter can make it look pretty.
BEGIN_KEY = '#begin'

with open(JSON_CONFIG, 'r') as f:
    data = json.load(f)

def get_replacement(key: str):
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


def render_line(line, context):
    matches = re.findall(r"{{\s*(.*?)\s*}}", line)
    modifiedLine = line
    for m in matches:
        replacement = get_replacement(m)
        modifiedLine = re.sub(r"\s*{{" + m + r"}}", replacement, line)
        print(modifiedLine)

    return modifiedLine;



def build_file(pageLayout: str):
    with open(HEADER_BASE, 'r') as header_in, open(HEADER_OUTPUT, 'w') as header_out:
        file_start = False
        for line in header_in:
            if BEGIN_KEY in line:
                file_start = True
            elif file_start:
                rendered = render_line(line, data)
                header_out.write(rendered)

    with open(FOOTER_BASE, 'r') as footer_in, open(FOOTER_OUTPUT, 'w') as footer_out:
        file_start = False
        for line in footer_in:
            if BEGIN_KEY in line:
                file_start = True
            elif file_start:
                rendered = render_line(line, data)
                footer_out.write(rendered)


build_file("site-specific")
