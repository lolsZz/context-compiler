import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from utils import fetch_repo_content, parse_github_url, InvalidGithubUrlError
from constants import GITHUB_API_URL, SUPPORTED_FILETYPES

def fetch_and_format_files(owner, repo, file_paths, token):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_repo_content, f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}", token) for path in file_paths]
        file_contents = [base64.b64decode(future.result()['content']).decode('utf-8') for future in tqdm(as_completed(futures), total=len(file_paths), desc="Processing files")]
    formatted_files = ""
    for path, content in zip(file_paths, file_contents):
        formatted_files += f"\n{path}:\n```\n{content}\n```\n"
    return formatted_files

def process_github_repo(owner, repo, token=None, use_cache=False):
    processed_files = []
    unsupported_files = []
    if use_cache:
        print(f"\nFetching repository information from cache.")
    else:
        print(f"\nFetching repository information from GitHub API.")
    try:
        readme_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/README.md"
        readme_info = fetch_repo_content(readme_url, token)
        readme_content = base64.b64decode(readme_info['content']).decode('utf-8')
        formatted_string = f"README.md:\n```\n{readme_content}\n```\n\n"
        processed_files.append("README.md")
    except FileNotFoundError:
        formatted_string = f"README.md: Not found or error fetching README\n\n"
    default_branch = "main"
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    tree_info = fetch_repo_content(url, token)
    file_paths = []
    for item in tree_info['tree']:
        if item['type'] == 'blob' and any(item['path'].endswith(ext) for ext in SUPPORTED_FILETYPES):
            file_paths.append(item['path'])
        else:
            unsupported_files.append(item['path'])
    formatted_files = fetch_and_format_files(owner, repo, file_paths, token)
    formatted_string += formatted_files
    processed_files.extend(file_paths)
    return formatted_string, processed_files, unsupported_files