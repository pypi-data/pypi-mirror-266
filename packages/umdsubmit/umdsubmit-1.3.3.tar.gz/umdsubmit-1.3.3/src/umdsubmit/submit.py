import os
import requests
import shutil
import getpass

def read_value_from_file(file_name, key):
    """
    Reads a value from a file given a key.

    Args:
        file_name (str): The name of the file to read from.
        key (str): The key to look for in the file.

    Returns:
        str: The value associated with the key.

    Raises:
        FileNotFoundError: If the file or the key is not found.
    """
    try:
        with open(file_name, "r") as f:
            for line in f:
                if line.startswith(key):
                    _, v = line.split('=')
                    return v.strip()
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return None

    print(f"Key '{key}' not found in file '{file_name}'.")
    return None

def get_info(lineStart):
    """
    Retrieves information from the .submit file based on a given line start.

    Args:
        lineStart (str): The starting line of the information to retrieve.

    Returns:
        str: The value associated with the line start.

    Raises:
        FileNotFoundError: If the line start is not found in the .submit file.
    """
    value = read_value_from_file(".submit", lineStart)
    if value is None:
        raise FileNotFoundError(f"Key '{lineStart}' not found in .submit file.")
    return value

def get_cvs_account():
    """
    Retrieves the CVS account from the .submitUser file.

    Returns:
        str: The CVS account.
    """
    return read_value_from_file(".submitUser", 'cvsAccount')

def get_one_time_password():
    """
    Retrieves the one-time password from the .submitUser file.

    Returns:
        str: The one-time password.
    """
    return read_value_from_file(".submitUser", 'oneTimePassword')

def walk_and_add_files(zip_writer):
    """
    Walks through the current directory and adds all files to a zip archive.

    Args:
        zip_writer (ZipFile): The zip writer object to add files to.
    """
    for folder, _, files in os.walk("."):
        for file in files:
            if file != ".submitUser":
                file_path = os.path.join(folder, file)
                with open(file_path, "rb") as f:
                    zip_writer.writestr(file_path, f.read())

def auth():
    """
    Authenticates the user by prompting for UMD Directory ID and password,
    and saves the authentication response to the .submitUser file.
    """
    print("Enter UMD Directory ID: ")
    username = input()
    password = getpass.getpass("Enter UMD Password: ")
    data = {"loginName" : username, "password" : password, "courseKey" : get_info("courseKey"), "projectNumber" : get_info("projectNumber")}
    url_part = f"/eclipse/NegotiateOneTimePassword"
    response = requests.post(get_info("baseURL") + url_part, data = data)
    f = open(".submitUser", "x")
    f.write(response.text)
    print(response.text)

def main():
    """
    Main function that creates a zip archive of the current directory,
    submits the archive to a specified URL, and prints the response.
    """
    if not os.path.isfile('.submitUser'):
        auth()
    shutil.make_archive('submit', 'zip', os.getcwd())
    submit_zip_object =  open('submit.zip', 'rb')
    files = {"submittedFiles": ("submit.zip", submit_zip_object)}
    data = {"courseName" : get_info("courseName"), "projectNumber" : get_info("projectNumber"), "semester" : get_info("semester"), "courseKey" : get_info("courseKey"), "authentication.type" : get_info("authentication.type"), "baseURL" : get_info("baseURL"), "submitURL" : get_info("submitURL"), "cvsAccount" : get_cvs_account(), "oneTimePassword" : get_one_time_password(), "submitClientTool" : "umdsubmit", "submitClientVersion" : "1.0"}
    response = requests.post(get_info("submitURL"), files = files, data = data)
    if response.status_code == 401:
        auth()
        main()
    print(response.text)
