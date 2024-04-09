import os
import lpb_lib

def find_code_in_env_file(path_w, code_to_find):    
    """
    Find a code in the .env file and return its value.
    Args:
    :path: The path to the .env file.
    :code_to_find: The code to find in the .env file.
    Returns:
        :value: The value of the code in the .env file.
    """
    if os.path.exists(f"{path_w}/.env"):
        with open(f"{path_w}/.env", 'r') as file:
            for line in file:
                if code_to_find in line:
                    value = line.split("= ")[1]
                    return value.replace('"', "").replace("\n", "")
    return None