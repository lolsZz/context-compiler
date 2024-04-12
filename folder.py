import os
from tqdm import tqdm
from utils import get_folder_files, get_file_content, log_unsupported_file

def process_folder(folder_path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name):
    formatted_string = ""
    processed_files = []
    unsupported_files = []

    # Generate the directory tree
    tree_output = generate_directory_tree(folder_path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name)
    formatted_string += tree_output

    print(f"\nProcessing folder: {folder_path}")
    for file_path in tqdm(list(get_folder_files(folder_path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name)), desc="Processing files"):
        try:
            content = get_file_content(file_path)
            if content is not None:
                formatted_string += f"\n{file_path}:\n```\n{content}\n```\n"
                processed_files.append(file_path)
            else:
                unsupported_files.append(file_path)
        except IOError as e:
            log_unsupported_file(file_path, str(e))
            unsupported_files.append(file_path)

    if not processed_files:
        print(f"\nNo files were processed in the folder: {folder_path}")

    return formatted_string, processed_files, unsupported_files

def generate_directory_tree(folder_path, exclusions, file_extensions, file_names, excluded_extensions, output_file_name, level=0):
    tree_output = ""
    scanned_files = []
    ignored_files = []
    unsupported_dirs = []

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in exclusions]
        indent = "│   " * level
        branch = "├── "
        pipe = "│   "

        if level == 0:
            tree_output += f"{os.path.basename(root)}/\n"
        else:
            tree_output += f"{indent}{branch}{os.path.basename(root)}/\n"

        for file in files:
            file_path = os.path.join(root, file)
            if file != output_file_name and file not in file_names and file.split('.')[-1] not in excluded_extensions:
                if not file_extensions or file.split('.')[-1] in file_extensions:
                    scanned_files.append(f"{indent}{pipe}+ {file}")
                else:
                    unsupported_dir = os.path.relpath(root, folder_path)
                    unsupported_dirs.append(unsupported_dir)
            else:
                ignored_files.append(f"{indent}{pipe}- {file}")


        for i, dir in enumerate(dirs):
            dir_path = os.path.join(root, dir)
            if i == len(dirs) - 1:
                tree_output += generate_directory_tree(dir_path, exclusions, file_extensions, file_names, excluded_extensions, level + 1).replace("├── ", "└── ", 1)
            else:
                tree_output += generate_directory_tree(dir_path, exclusions, file_extensions, file_names, excluded_extensions, level + 1)

    if scanned_files:
        tree_output += "\n".join(scanned_files) + "\n\n"

    if ignored_files:
        tree_output += "Ignored Files:\n"
        tree_output += "\n".join(ignored_files) + "\n\n"

    if unsupported_dirs:
        tree_output += "Unsupported Directories:\n"
        for dir in set(unsupported_dirs):
            unsupported_count = sum(1 for file in os.listdir(os.path.join(folder_path, dir)) if file.split('.')[-1] not in file_extensions)
            tree_output += f"{indent}{pipe}{dir}/ ({unsupported_count} unsupported files)\n"
        tree_output += "\n"

    return tree_output
