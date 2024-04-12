import os
import requests
import subprocess
from urllib.parse import urlparse
from colorama import Fore, Style

class InvalidGithubUrlError(ValueError):
    pass

def parse_github_url(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip("/").split("/")
    if len(path_segments) >= 2:
        return path_segments[0], path_segments[1]
    raise InvalidGithubUrlError(f"Invalid GitHub URL provided: {url}")

def fetch_repo_content(url, token=None):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        raise FileNotFoundError(f"File not found: {url}")
    response.raise_for_status()
    return response.json()

def check_if_git_repo():
    return os.path.isdir('.git')

def extract_git_url():
    result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        git_url = result.stdout.strip()
        if git_url.startswith("git@github.com:"):
            git_url = git_url.replace("git@github.com:", "https://github.com/")
        elif git_url.startswith("https://github.com/"):
            pass
        else:
            return None
        return git_url.rstrip('.git')
    return None

def log_unsupported_file(file_path, reason):
    print(f"{Fore.YELLOW}[Unsupported File] {file_path} - {reason}{Style.RESET_ALL}")

def get_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        log_unsupported_file(file_path, "Encoding error")
        return None

def get_folder_files(folder_path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name):
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in exclusions]
        for file in files:
            if file != output_file_name and file not in file_names and file.split('.')[-1] not in excluded_extensions:
                if not file_extensions or file.split('.')[-1] in file_extensions:
                    yield os.path.join(root, file)
