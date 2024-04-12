import os
import inquirer
from colorama import init, Fore, Style
from github import process_github_repo, InvalidGithubUrlError
from folder import process_folder
from utils import check_if_git_repo, extract_git_url, get_folder_files, parse_github_url
from constants import SUPPORTED_FILETYPES, DEFAULT_EXCLUSIONS, DEFAULT_EXTENSION_EXCLUSIONS

init()  # Initialize colorama for color output

def display_summary(execution_mode, repo_or_folder, processed_files, unsupported_files, output_file_name):
    # ... (no changes)
    print(f"{Fore.CYAN}🌟 Context Compiler Summary 🌟")
    print(f"{Fore.CYAN}==================================\n")
    print(f"{Fore.BLUE}Execution Mode:{Style.RESET_ALL} {execution_mode}")
    print(f"{Fore.BLUE}Repository or Folder:{Style.RESET_ALL} {repo_or_folder}")
    print(f"{Fore.BLUE}Files Processed:{Style.RESET_ALL} {len(processed_files)}")
    print(f"{Fore.BLUE}Supported Files:{Style.RESET_ALL} {len(processed_files) - len(unsupported_files)}")
    print(f"{Fore.BLUE}Unsupported Files:{Style.RESET_ALL} {len(unsupported_files)}")
    for file in processed_files:
        print(f"{Fore.GREEN}✅ {file} processed successfully")
    for file in unsupported_files:
        print(f"{Fore.YELLOW}❌ {file} skipped (unsupported file type)")
    output_size_mb = os.path.getsize(output_file_name) / (1024 * 1024)
    print(f"\n{Fore.BLUE}Formatted context saved to:{Style.RESET_ALL} {output_file_name}")
    print(f"{Fore.BLUE}Output size:{Style.RESET_ALL} {output_size_mb:.2f} MB")
    print(f"\n{Fore.GREEN}Thank you for using the Context Compiler! 😊")

def handle_github_auto():
    if check_if_git_repo():
        git_url = extract_git_url()
        if git_url:
            try:
                owner, repo = parse_github_url(git_url)
                token = os.environ.get('GITHUB_ACCESS_TOKEN')
                formatted_repo_info, processed_files, unsupported_files = process_github_repo(owner, repo, token, use_cache=True)
                output_file_name = f"{repo}-formatted-prompt.txt"
                with open(output_file_name, 'w', encoding='utf-8') as file:
                    file.write(formatted_repo_info)
                print(f"\n{Fore.GREEN}Repository information has been saved to {output_file_name}")
                display_summary("GitHub Auto", f"{owner}/{repo}", processed_files, unsupported_files, output_file_name)
            except InvalidGithubUrlError as e:
                print(f"\n{Fore.RED}{str(e)}")
        else:
            print(f"\n{Fore.RED}GitHub URL could not be extracted.")
    else:
        print(f"\n{Fore.RED}Not a valid git repository.")

def handle_github_url():
    questions = [
        inquirer.Text('url', message="Enter the GitHub URL"),
    ]
    answers = inquirer.prompt(questions)
    git_url = answers['url']
    try:
        owner, repo = parse_github_url(git_url)
        token = os.environ.get('GITHUB_ACCESS_TOKEN')
        formatted_repo_info, processed_files, unsupported_files = process_github_repo(owner, repo, token, use_cache=True)
        output_file_name = f"{repo}-formatted-prompt.txt"
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(formatted_repo_info)
        print(f"\n{Fore.GREEN}Repository information has been saved to {output_file_name}")
        display_summary("GitHub URL", f"{owner}/{repo}", processed_files, unsupported_files, output_file_name)
    except InvalidGithubUrlError as e:
        print(f"\n{Fore.RED}{str(e)}")

def handle_folder_scan():
    folder_questions = [
        inquirer.List('folder_option',
                      message="Select folder option:",
                      choices=['Current Folder', 'Select Child Folders'],
                      ),
    ]
    folder_answers = inquirer.prompt(folder_questions)
    folder_path = get_folder_path(folder_answers)
    exclusions, file_extensions, file_names = prompt_user_for_exclusions_and_extensions()
    
    output_file_name = ""  # Initialize with an empty string
    if isinstance(folder_path, list):
        output_file_name = f"{os.path.basename(folder_path[0])}-formatted-prompt.txt"
    else:
        output_file_name = f"{os.path.basename(folder_path)}-formatted-prompt.txt"
    output_file_name = handle_existing_file(output_file_name)
    
    excluded_extensions = prompt_unsupported_file_types(folder_path, exclusions, file_extensions, file_names, DEFAULT_EXTENSION_EXCLUSIONS, output_file_name)
    process_and_display_folder_summary(folder_path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name)

def get_folder_path(folder_answers):
    if folder_answers['folder_option'] == 'Current Folder':
        return os.getcwd()
    else:
        current_folder = os.getcwd()
        child_folders = [f for f in os.listdir(current_folder) if os.path.isdir(os.path.join(current_folder, f))]
        folder_questions = [
            inquirer.Checkbox('selected_folders',
                              message="Select child folders to include:",
                              choices=child_folders,
                              ),
        ]
        folder_answers = inquirer.prompt(folder_questions)
        return [os.path.join(current_folder, folder) for folder in folder_answers['selected_folders']]

def prompt_user_for_exclusions_and_extensions():
    default_exclusions = ','.join(DEFAULT_EXCLUSIONS)
    exclusions = input(f"{Fore.BLUE}Enter folders to exclude (comma-separated) [{default_exclusions}]:{Style.RESET_ALL} ")
    if not exclusions.strip():
        exclusions = default_exclusions
    exclusions = [e.strip() for e in exclusions.split(',') if e.strip()]
    file_extensions = input(f"{Fore.BLUE}Enter file extensions to include (comma-separated) or leave empty to include all:{Style.RESET_ALL} ").split(',')
    file_extensions = [e.strip() for e in file_extensions if e.strip()]
    file_names = input(f"{Fore.BLUE}Enter file names to exclude (comma-separated) or leave empty to exclude none:{Style.RESET_ALL} ").split(',')
    file_names = [e.strip() for e in file_names if e.strip()]
    return exclusions, file_extensions, file_names

def prompt_unsupported_file_types(folder_path, exclusions, file_extensions, file_names, default_extension_exclusions, output_file_name):
    unique_extensions = get_unique_extensions(folder_path, exclusions, file_extensions, file_names, output_file_name)
    if not unique_extensions:
        return []
    extension_info = []
    total_files = 0
    total_size_mb = 0
    for extension in unique_extensions:
        files = list(get_folder_files(folder_path, exclusions, [extension], file_names, default_extension_exclusions, output_file_name))
        count = len(files)
        size_mb = sum(os.path.getsize(file_path) for file_path in files) / (1024 * 1024)
        extension_info.append({
            'extension': extension,
            'count': count,
            'size_mb': size_mb,
            'supported': extension in SUPPORTED_FILETYPES
        })
        total_files += count
        total_size_mb += size_mb

    supported_extensions = [f"{info['extension']} ({info['count']} files - {info['size_mb']:.2f}MB)" for info in extension_info if info['supported']]
    unsupported_extensions = [f"{info['extension']} ({info['count']} files - {info['size_mb']:.2f}MB)" for info in extension_info if not info['supported']]

    supported_files = sum(info['count'] for info in extension_info if info['supported'])
    unsupported_files = sum(info['count'] for info in extension_info if not info['supported'])

    print(f"\nTotal files: {total_files} - Total size: {total_size_mb:.2f}MB")
    print(f"Supported files: {supported_files} - Unsupported files: {unsupported_files}\n")

    extension_questions = [
        inquirer.Checkbox('excluded_extensions',
                          message="Select the file extensions to exclude:",
                          choices=unsupported_extensions + [''] + supported_extensions,
                          default=[info['extension'] for info in extension_info if not info['supported']],
                          ),
    ]
    extension_answers = inquirer.prompt(extension_questions)
    return extension_answers['excluded_extensions']

def get_unique_extensions(folder_path, exclusions, file_extensions, file_names, output_file_name):
    unique_extensions = set()
    if isinstance(folder_path, list):
        for path in folder_path:
            for file_path in get_folder_files(path, exclusions, file_extensions, file_names, [], output_file_name):
                extension = os.path.splitext(file_path)[1]
                unique_extensions.add(extension)
    else:
        for file_path in get_folder_files(folder_path, exclusions, file_extensions, file_names, [], output_file_name):
            extension = os.path.splitext(file_path)[1]
            unique_extensions.add(extension)
    return unique_extensions


def process_and_display_folder_summary(folder_path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name):
    if isinstance(folder_path, list):
        for path in folder_path:
            output_file_name = f"{os.path.basename(path)}-formatted-prompt.txt"
            output_file_name = handle_existing_file(output_file_name)
            formatted_folder_info, processed_files, unsupported_files = process_folder(path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name)
            with open(output_file_name, 'w', encoding='utf-8') as file:
                file.write(formatted_folder_info)
            print(f"\n{Fore.GREEN}Folder information has been saved to {output_file_name}")
            display_summary("Folder Scan", path, processed_files, unsupported_files, output_file_name)
    else:
        formatted_folder_info, processed_files, unsupported_files = process_folder(folder_path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name)
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(formatted_folder_info)
        print(f"\n{Fore.GREEN}Folder information has been saved to {output_file_name}")
        display_summary("Folder Scan", folder_path, processed_files, unsupported_files, output_file_name)

def handle_existing_file(file_name):
    if os.path.exists(file_name):
        print(f"\n{Fore.YELLOW}The file '{file_name}' already exists.")
        overwrite = input(f"{Fore.BLUE}Do you want to overwrite the existing file? (y/n): {Style.RESET_ALL}")
        if overwrite.lower() == 'y':
            return file_name
        else:
            new_file_name = input(f"{Fore.BLUE}Enter a new file name: {Style.RESET_ALL}")
            return handle_existing_file(new_file_name)
    return file_name
        
def main():
    questions = [
        inquirer.List('mode',
                      message="Select execution mode:",
                      choices=['GitHub Auto', 'GitHub URL', 'Folder Scan'],
                      ),
    ]
    answers = inquirer.prompt(questions)
    if answers['mode'] == 'GitHub Auto':
        handle_github_auto()
    elif answers['mode'] == 'GitHub URL':
        handle_github_url()
    elif answers['mode'] == 'Folder Scan':
        handle_folder_scan()

if __name__ == "__main__":
    main()
