import re
import json
import os
import shutil
import requests
from dotenv import load_dotenv
from datetime import datetime

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

SITE_SPECIFIC_HEADER_BASE = './site_specific/site_specific_header_base.html' 
SITE_SPECIFIC_FOOTER_BASE = './site_specific/site_specific_footer_base.html'

SITE_MAIN_HEADER_BASE = './site_main/site_main_header_base.html' 
SITE_MAIN_FOOTER_BASE = './site_main/site_main_footer_base.html'

LOCAL = 0
T4DEV = 1
T4PROD = 2

# Sometimes the file needs some tags at the top to balance out what it contains so the formatter can make it look pretty.
BEGIN_KEY = '#begin'
ALL = 'a';

def get_replacement(page_layout: str, data: dict, key: str):
    if key == "header_mb-4":
        # check if true or false. If true, return "mb-4", which will place a margin below the header
        if data[key]:
            return " mb-4"
        else:
            return ""

    elif key == "header_mb-md-5":
        # check if true or false. If true, return " mb-4", which will place a margin below the header
        if data[key]:
            return " mb-md-5"
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


def build_file(page_layout: str, header_base: str, footer_base: str):

    # get generate date and time
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    generate_statement = "<!-- File was automatically generated at " + formatted + " -->\n"

    # create build tree
    json_config = './' + page_layout + '/config.json'
    output_dir = f'build/{page_layout}'
    os.makedirs(output_dir, exist_ok=True)  # create dir if it doesn't exist

    header_output = os.path.join(output_dir, 'header.html')
    footer_output = os.path.join(output_dir, 'footer.html')

    with open(json_config, 'r') as f:
        data = json.load(f)

    # build files
    with open(header_base, 'r') as header_in, open(header_output, 'w') as header_out:
        header_out.write(generate_statement)
        file_start = False
        for line in header_in:
            if BEGIN_KEY in line:
                file_start = True
            elif file_start:
                rendered = render_line(page_layout, data, line, data)
                header_out.write(rendered)

    with open(footer_base, 'r') as footer_in, open(footer_output, 'w') as footer_out:
        footer_out.write(generate_statement)
        file_start = False
        for line in footer_in:
            if BEGIN_KEY in line:
                file_start = True
            elif file_start:
                rendered = render_line(page_layout, data, line, data)
                footer_out.write(rendered)

def upload_file(page_layout: str, build_location: int):
    load_dotenv()

    auth_token = ""
    base_url = ""

    json_config = './' + page_layout + '/config.json'
    
    with open(json_config, 'r') as f:
        data = json.load(f)
    
    page_layout_id = data["page_layout_id"]
    page_layout_name = data["page_layout_name"]
    page_layout_description = data["description"]

    if build_location == T4DEV:
        auth_token = os.getenv("T4DEV_AUTH_TOKEN")
        base_url = "https://t4dev.scu.edu/terminalfour/rs/pageLayout/"

    elif build_location == T4PROD:
        auth_token = os.getenv("T4PROD_AUTH_TOKEN")
        # base_url = "https://t4.scu.edu/terminalfour/rs/pageLayout/"
    else:
        raise ValueError("Invalid build location")

    if not auth_token:
        raise ValueError("auth_token environment variable is not set")

    headerCode = ""
    footerCode = ""

    json_config = './' + page_layout + '/config.json'
    
    with open(json_config, 'r') as f:
        data = json.load(f)
    
    page_layout_id = data["page_layout_id"]

    print(page_layout_id)

    base_url += str(page_layout_id)

    output_dir = f'build/{page_layout}'

    header_file_path = os.path.join(output_dir, 'header.html')
    footer_file_path = os.path.join(output_dir, 'footer.html')

    header_content = ""
    footer_content = ""

    with open(header_file_path, 'r', encoding='utf-8') as f:
        header_content = f.read()
    
    with open(footer_file_path, 'r', encoding='utf-8') as f:
        footer_content = f.read()

    payload = json.dumps({
        "name": str(page_layout_name),
        "description": str(page_layout_description),
        "syntaxType": 0,
        "status": 0,
        "headerCode": str(header_content),
        "footerCode": str(footer_content),
        "stylesheetCode": "",
        "fileExtension": "",
        "contentLayout": "",
        "currentVersion": "3.0",
        "language": "en",
        "layoutProcessor": 1,
        "typeContent": "pageLayout",
        "showOwner": False,
        "id": str(page_layout_id),
        "editable": True,
        "sharedGroupCount": 0,
        "sharedGroups": [],
        "fullAccess": True
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_token
    }

    response = requests.request("PUT", base_url, headers=headers, data=payload)

    print(response.text)

def main():
    upload_location = LOCAL

    header_base = ""
    footer_base = ""

    # remove build tree
    build_root = 'build'
    if os.path.exists(build_root):
        shutil.rmtree(build_root)
    os.makedirs(build_root, exist_ok=True)

    make_options = [
        "Build locally",
        "Build locally and upload to T4 dev",
        "Build locally and upload to T4 production"
    ]

    print("What to do with the files?")

    for i, b in enumerate(make_options):
        print(i, "-", b)

    selection = int(input("Choose a make option: "))

    if selection == LOCAL:
        print(bcolors.OKBLUE + "Changes will not be uploaded" + bcolors.ENDC)
    elif selection == T4DEV:
        print(bcolors.OKBLUE + "Changes will be uploaded to T4 dev" + bcolors.ENDC)
    elif selection == T4PROD:
        print(bcolors.WARNING + "WARNING: Changes will be uploaded to T4 production")
    else:
        raise ValueError("Invalid make option")

    upload_location = selection

    build_options = {
        # Site Specific build options
        "Site Specific": "site_specific/site_specific",
        "Site Specific: Cover Image": "site_specific/site_specific_cover_image",
        "Site Specific: Full Width": "site_specific/site_specific_full_width",
        "Site Specific: Landing Page": "site_specific/site_specific_landing_page",
        "Site Specific: Mobile Optimized": "site_specific/site_specific_mobile_optimized",
        "Site Specific: Sidebar Breakout Landing":
        "site_specific/site_specific_sidebar_breakout_landing",

        # Site Main build options
        "Site Main: Cover Image": "site_main/site_main_cover_image",
        "Site Main: Full Width": "site_main/site_main_full_width",
        "Site Main: Inner": "site_main/site_main_inner",
        "Site Main: Landing Page": "site_main/site_main_landing_page",
        "Site Main: Mobile Optimized": "site_main/site_main_mobile_optimized",
        "Site Main: Sidebar Breakout Landing": "site_main/site_main_sidebar_breakout_landing"
    }

    print("Which file to build?")

    options_list = list(build_options.keys())

    for i, b in enumerate(options_list):
        print(i, "-", b)
    print(ALL,  "- All files")

    selection = input("Pick page layout: ")  # input() takes one argument: the prompt

    if (selection == ALL):
        for option in build_options:
            if "Site Specific" in option:
                header_base = SITE_SPECIFIC_HEADER_BASE
                footer_base = SITE_SPECIFIC_FOOTER_BASE
            elif "Site Main" in option:
                header_base = SITE_MAIN_HEADER_BASE
                footer_base = SITE_MAIN_FOOTER_BASE

            selected_value = build_options[option]

            print("Building", selected_value)
            build_file(selected_value, header_base, footer_base)

            if upload_location != LOCAL:
                upload_file(selected_value, upload_location)

        print(bcolors.OKGREEN + "Finished generating all files.")
    else:
        if int(selection) < 0 or int(selection) >= len(build_options):
            print(bcolors.FAIL + "FAIL: Invalid choice. Aborting process!")
            raise ValueError("Check if input is valid")

        selected_key = options_list[int(selection)]
        selected_value = build_options[selected_key]

        if "Site Specific" in selected_key:
            header_base = SITE_SPECIFIC_HEADER_BASE
            footer_base = SITE_SPECIFIC_FOOTER_BASE
        elif "Site Main" in selected_key:
            header_base = SITE_MAIN_HEADER_BASE
            footer_base = SITE_MAIN_FOOTER_BASE

        print("Building " + selected_value)
        build_file(selected_value, header_base, footer_base)

        if upload_location != LOCAL:
            upload_file(selected_value, upload_location)

        print("Finished generating " + selected_value + " files.")


if __name__ == "__main__":
    main()
