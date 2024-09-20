import sys
import os
import json
import re
import random
from urllib import request

# url for prompt api on local machine
url_prompt = "http://127.0.0.1:8188/prompt"

# defined placeholders
prompt_placeholder = "__PROMPT_PLACEHOLDER__"
filename_placeholder = "__FILENAME_PLACEHOLDER__"
seed_placeholder = "__SEED_PLACEHOLDER__"


def sanitize_filename(s):
    # remove all special characters from string to make it a valid filename
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    max_length = 128
    if len(s) > max_length:
        s = s[:max_length]
    return s


def queue_prompt(prompt_text):
    p = {"prompt": json.loads(prompt_text)}
    data = json.dumps(p).encode('utf-8')
    req = request.Request(url_prompt, data=data)
    response = request.urlopen(req)
    return response


def main():
    # Argument validation
    if len(sys.argv) != 3:
        print("Usage: python generate_images.py <workflow.json> <prompts.txt>")
        sys.exit(1)

    workflow_file = sys.argv[1]
    prompts_file = sys.argv[2]

    # Check if the files exist
    if not os.path.isfile(workflow_file):
        print(f"Error: Cannot find workflow file '{workflow_file}'")
        sys.exit(1)

    if not os.path.isfile(prompts_file):
        print(f"Error: Cannot find prompts file '{prompts_file}'")
        sys.exit(1)

    # 1. Load the workflow file and the workflow file should be saved as api format
    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_text = f.read()

    # 2. Check if the workflow file contains the placeholders
    if prompt_placeholder not in workflow_text:
        print(f"No '{prompt_placeholder}' placeholder found in '{workflow_file}'")

    if seed_placeholder not in workflow_text:
        print(f"No '{seed_placeholder}' placeholder found in '{workflow_file}'")

    # 3. Load the prompts file
    with open(prompts_file, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]

    # 4. Read prompts from the prompts file line by line
    for prompt_text in prompts:
        # Carefully handle the prompt text to avoid breaking the JSON structure
        escaped_prompt = json.dumps(prompt_text)[1:-1]

        # Replace the prompt placeholder with the prompt text
        prompt_json_text = workflow_text.replace(prompt_placeholder, escaped_prompt)

        # Generate a random seed value and replace the seed placeholder
        seed_value = random.randint(0, 2**32 - 1)
        prompt_json_text = prompt_json_text.replace(seed_placeholder, str(seed_value))

        # Replace the filename placeholder with a sanitized version of the prompt text
        if filename_placeholder in prompt_json_text:
            safe_prompt = sanitize_filename(prompt_text)
            prompt_json_text = prompt_json_text.replace(filename_placeholder, safe_prompt)
        else:
            safe_prompt = sanitize_filename(prompt_text)

        # Send the prompt to the queue
        try:
            response = queue_prompt(prompt_json_text)
            response_data = response.read().decode('utf-8')
            res_json = json.loads(response_data)
            print(str(res_json))
        except Exception as e:
            print(f"Error sending prompt to queue: {e}, sent prompt: {prompt_json_text}")
            continue


if __name__ == '__main__':
    main()
