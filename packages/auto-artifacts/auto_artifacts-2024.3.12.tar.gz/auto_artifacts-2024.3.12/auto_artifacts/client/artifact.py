import os
import json
import shutil
import requests

def upload(base_url, file_paths, path, api_key=""):
    """
    Uploads files to the FastAPI server.

    Args:
        base_url (str): The base URL where the FastAPI server is running.
        file_paths (list of str): List of file paths of the files to be uploaded.
        path (str): The path where the files should be uploaded on the server.
        password (str): The password for accessing the upload functionality.

    Returns:
        bool: True if the files were uploaded successfully, False otherwise.
    """

    # The URL for the upload endpoint
    url = f"{base_url}/artifacts/upload/files?api_key={api_key}"

    # Prepare the files for uploading
    files = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            files.append(('files', (open(file_path, 'rb'))))
        else:
            return f"Error: file does not exist locally {file_path}"

    # Data to be sent in the form
    data = {
        'path': path,
        'api_key': api_key,
    }

    # Make the POST request to upload the files
    response = requests.post(url, files=files, data=data)
    return response.text

def download(base_url, filename, path, api_key=""):
    """
    Downloads a file from the FastAPI server.

    Args:
        base_url (str): The base URL where the FastAPI server is running.
        filename (str): The name of the file to download.
        path (str): The path to the file, relative to the base path on the server.
        password (str, optional): The password for accessing private files. Defaults to None.

    Returns:
        bool: True if the file was downloaded successfully, False otherwise.
    """
    # Construct the full URL for the download endpoint
    url = f"{base_url}/artifacts/download/file"

    # Parameters to be sent in the query string
    params = {
        'filename': filename,
        'path': path,
    }

    # Include the password in the parameters if it's provided
    params['api_key'] = api_key

    # Make the GET request to download the file
    response = requests.get(url, params=params)

    if response.ok:
        # If the request was successful, save the file
        with open(filename, 'wb') as file:
            file.write(response.content)
        return "success."
    else:
        return json.loads(response.text)['detail']

def move(src_path, dst_path):

    print("Moving artifact...")
    shutil.move(src_path, dst_path)
    print("Moving artifact...done.")

def zip(src_path, dst_path):
    base = os.path.basename(dst_path)
    name = base.split('.')[0] + base.split('.')[1]
    format = "zip"
    archive_from = os.path.dirname(src_path)
    archive_to = os.path.basename(src_path.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name,format), dst_path)


def extract(src_path, dst_path):

    print("Extracting artifact...")
    shutil.unpack_archive(src_path, dst_path, "zip")
    print("Extracting artifact...done.")

def push(env_path, org, project, version, branch_name, commit_hash, platform, artifact_path_local):

    global url

    # Construct deploy path
    artifact = os.path.basename(artifact_path_local)
    artifact_path_remote = f"{org}/{project}/{version}/{branch_name}/{commit_hash}/{platform}"
    print(f"Deploying {artifact_path_remote}/{artifact}...", end="")

    try:
        # Load URL
        with open(env_path, 'r') as j:
            raw = j.read()
        env = json.loads(raw)
        url = env["url"]
        api_key = env['api_key']
    except Exception as e:
        raise Exception(f"error: {e}")

    try:
        print(upload(url, [artifact_path_local], artifact_path_remote, api_key).replace('"',''))
        return True
    except Exception as e:
        raise Exception(f"error: {e}")

    return False

def pull(env_path, org, project, version, branch_name, commit_hash, platform, artifact_dir_local, artifact):

    global url

    # Construct deploy path
    artifact_path_remote = f"{org}/{project}/{version}/{branch_name}/{commit_hash}/{platform}"
    print(f"Pulling {artifact_path_remote}/{artifact}...", end="")

    try:
        # Load credentials
        with open(env_path, 'r') as j:
            raw = j.read()
        env = json.loads(raw)
        url = env["url"]
        api_key = env['api_key']
    except Exception as e:
        print(f"error: {str(e)}")

    try:
        # Deploy artifact
        curr_dir = os.getcwd()
        os.chdir(artifact_dir_local)
        print(download(url, artifact, artifact_path_remote, api_key).replace('"',''))
        os.chdir(curr_dir)
        return True
    except Exception as e:
        print(f"error: {str(e)}")

    return False