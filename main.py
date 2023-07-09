import sys
import datetime

from os import listdir
from os.path import isfile, join

import re

TOTAL_COUNT_EX_STR = "inventory count item = 0"
ERROR_STR = "error"

def get_id_price(string: str):
    id_match = re.search(r'\[(\d+)\]', string)
    price_match = re.search(r'\$(\d+(\.\d+)?)', string)

    if id_match and price_match:
        id_value = id_match.group(1)
        price_value = float(price_match.group(1))
        return id_value, price_value

    elif id_match and not price_match:
        id_value_except = id_match.group(1)
        return f"{id_value_except} inventory count item", '0'

    else:
        print("None")
        print(string)
        return None, None

def write_file(profiles: list[str], file_name: str):
    # Extract the list of ID-price pairs from the strings
    id_price_list = [get_id_price(string) for string in profiles]

    # Print the list of ID-price pairs
    # for id_price in id_price_list:
    #     id_value, price_value = id_price
    #     print(f"{id_value} - {price_value}")

    with open(f"sorted_with_price_{file_name}", "x") as created_file:
        for id_price in id_price_list:
            id_value, price_value = id_price
            created_file.write(f"{id_value} - {price_value}\n")

    with open(f"sorted_only_id_{file_name}", "x") as created_file:
        for id_price in id_price_list:
            id_value, price_value = id_price
            created_file.write(f"{id_value}\n")

# Define a function to extract and convert the price value
def get_price(string):
    try:
        price = re.findall(r'\$([\d.]+)', string)[0]
        return float(price)
    except:
        # For case when `inventory count item = 0` in logger.txt
        return float(0)

def sort_profiles(profiles: list[str]):
    # Sort the list of strings based on price in ascending order
    sorted_strings = sorted(profiles, key=get_price, reverse=True)

    # Print the sorted strings
    # for sorted_string in sorted_strings:
    #     print(sorted_string)

    return sorted_strings

def analyze(profiles: list[str]):
    filtered_profiles = []
    
    for profile in profiles:
        # Extract the inventory price from the profile
        is_price: bool = len(profile.split("$")) >=2
        is_special_ex_str: bool = TOTAL_COUNT_EX_STR in profile

        if is_price or is_special_ex_str:

            if is_special_ex_str:
                filtered_profiles.append(profile)
                continue

            inventory_price = float(profile.strip().split("$")[1])

            # Check if the inventory price is greater than $100
            if inventory_price >= float(sys.argv[1]) and inventory_price <= float(sys.argv[2]):
                # Extract the profile without the inventory amount
                profile_without_inventory = profile.split("with")[0].strip()
                if ERROR_STR in profile_without_inventory:
                    continue

                filtered_profiles.append(profile)

    # Print the filtered profiles
    # for profile in filtered_profiles:
    #     print(profile)

    return filtered_profiles

def analyze_logs_folder(logs_folder: str):
    only_files = [f for f in listdir(logs_folder) if isfile(join(logs_folder, f))]
    all_profiles = []

    for file in only_files:
        with open(f"{logs_folder}/{file}") as f:
            data = f.readlines()
            profiles = analyze(data)
            sorted_profiles = sort_profiles(profiles)
            all_profiles += sorted_profiles

    sorted_all_profiles = sort_profiles(all_profiles)
    time_now  = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S') 
    write_file(sorted_all_profiles, f"between_{sys.argv[1]}_{sys.argv[2]}_time_{time_now}.txt")

if __name__ == "__main__":
    print(sys.argv[1])
    print(sys.argv[2])

    logs_folder = "./logs"
    analyze_logs_folder(logs_folder)