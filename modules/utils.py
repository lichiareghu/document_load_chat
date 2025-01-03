import os
import json
from ast import literal_eval
from datetime import datetime
from config import Config
from unidecode import unidecode

def get_filepath(target_file,target_directory):

    # Define the root directory (adjust as needed, e.g., os.getcwd() for current directory)
    root_directory = os.getcwd()
    # Search for the file in the root directory and its subdirectories
    target_path = full_path = None
    for dirpath, dirnames, filenames in os.walk(root_directory):
        if target_directory in dirnames:
            target_path = os.path.join(dirpath, target_directory)
            break
    if target_path:
        full_path = os.path.join(target_path, target_file)
    return full_path

def build_json(data_list2, company_name):

    today_date = datetime.now().strftime("%d-%m-%Y")
    title = f"ESG Report for the company {company_name}"
    data_list=[]
    json_data={}
    for data in data_list2:
        data_list.append(data[list(data.keys())[0]])
    intro=[item for item in data_list if item['details']['name']=="Introduction"]
    sec_key = 1
    if len(intro)>0:
        json_data = {str(sec_key):{"title":intro[0]['details']['name'], "content": intro[0]['content']}}
        sec_key = +1
    qstns=[data for data in data_list if data['details']['name']=='Question']
    categories = list(set([data['details']['question']['category']['name'] for data in qstns]))

    json_data = {str(sec_key): {}}
    ss = 1  # Counter for subsections within each category

    for cat in categories:
        # Initialize the category structure
        json_data[str(sec_key)]['title'] = cat
        json_data[str(sec_key)].setdefault('subsections', {})

        subsections = {}
        sss = 1  # Counter for questions within each standard
        previous_std = None  # Track the previous standard

        for idx, data in enumerate(qstns):

            if cat == data['details']['question']['category']['name']:

                # Create the standard structure
                std_code = data['details']['question']['ESRS_standard']['code']
                std_name = data['details']['question']['ESRS_standard']['name']
                std = f"{std_code} {std_name}"
                # Check if the standard has changed
                if previous_std and std != previous_std:
                    # Increment ss only when std changes
                    ss += 1
                    sss=1
                    previous_std = std  # Update the previous standard
                # Set the std key
                std_key = f"{sec_key}.{ss}"

                # Ensure the standard exists
                if std_key not in subsections:
                    subsections[std_key] = {'title': std, 'questions': {}}

                # Add the question under the standard
                question_key = f"{std_key}.{sss}"
                subsections[std_key]['questions'][question_key] = {
                    'question': data['details']['question']['question_text'],
                    'content': unidecode(data['content']),
                }

                sss += 1

        # Update the JSON data with the collected subsections for this category
        json_data[str(sec_key)]['subsections'].update(subsections)

    return json_data

def load_json_file(path):
    try:
        data = None
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return data
    except PermissionError:
        return data

def save_results(data):
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create the filename
    filename = f"results_{timestamp}.txt"
    path = os.path.join(Config.RESULTS_DIR, filename)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    return "Saved results successfully"

def delete_results(path):
    try:
        os.remove(path)
    except Exception as e:
        print(f"Failed to delete file {path}: {e}")




