'''
project_handler.py
'''

import os
import shutil
import pathlib

from infiltra.utils import BOLD_RED,BOLD_GREEN, BOLD_YELLOW, BOLD_CYAN


# Define the base directory for storing application data
app_data_directory = pathlib.Path.home().joinpath('.config', 'infiltra')

# Ensure the directory exists
app_data_directory.mkdir(parents=True, exist_ok=True)

# Define the path for last_project.txt
last_project_file_path = app_data_directory.joinpath('last_project.txt')


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Base projects directory path
projects_base_path = os.path.expanduser('~/projects')


def create_ips_file(project_path):
    create_file = input(
        f"{BOLD_YELLOW}Would you like to create an ips.txt file in this project? (Y/n): ").strip().lower()
    if create_file in ['', 'y', 'yes']:
        ips_file_path = os.path.join(project_path, 'ips.txt')
        print(f"{BOLD_GREEN}Please enter the IPs (one per line). Press CTRL+D when done:")
        try:
            with open(ips_file_path, 'w') as ips_file:
                while True:
                    try:
                        ip = input()
                        ips_file.write(ip + '\n')
                    except EOFError:  # This is triggered by pressing CTRL+D or CTRL+Z
                        break
            print(f"{BOLD_GREEN}ips.txt file has been created in {ips_file_path}")
        except Exception as e:
            print(f"{BOLD_RED}An error occurred while creating ips.txt: {e}")
    else:
        print(f"{BOLD_YELLOW}Skipping ips.txt file creation.")


def create_project_directory(org_name):
    clear_screen()
    project_path = os.path.join(projects_base_path, org_name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print(f"{BOLD_GREEN}Created project directory for '{org_name}' at {project_path}")
        create_ips_file(project_path)
    else:
        print(f"{BOLD_YELLOW}Project directory for '{org_name}' already exists at {project_path}")
    return project_path


def save_last_project(project_name):
    clear_screen()
    with last_project_file_path.open('w') as file:
        file.write(project_name)


def load_project():
    clear_screen()
    projects = list_projects()
    if not projects:
        print(f"{BOLD_RED}There are no projects to load.")
        return None

    print(f"{BOLD_CYAN}Available Projects:")
    for idx, project in enumerate(projects, start=1):
        print(f"{BOLD_GREEN}{idx}. {project}")

    choice = input(f"{BOLD_YELLOW}Enter the number of the project to load: ").strip()
    if choice.isdigit():
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(projects):
            org_name = projects[choice_idx]
            project_path = os.path.join(projects_base_path, org_name)
            print(f"{BOLD_GREEN}Loaded project for '{org_name}'.")
            return project_path
        else:
            print(f"{BOLD_RED}Invalid project number.")
    else:
        print(f"{BOLD_RED}Please enter a valid number.")
    return None


def delete_project():
    clear_screen()
    projects = list_projects()
    if not projects:
        print(f"{BOLD_RED}There are no projects to delete.")
        return None

    print(f"{BOLD_CYAN}Available Projects:")
    for idx, project in enumerate(projects, start=1):
        print(f"{BOLD_GREEN}{idx}. {project}")

    choice = input(f"{BOLD_YELLOW}Enter the number of the project to delete: ").strip()
    if choice.isdigit():
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(projects):
            org_name = projects[choice_idx]
            confirm = input(
                f"{BOLD_RED}Are you sure you want to delete the project '{org_name}'? (y/N): ").strip().lower()
            if confirm == 'y':
                project_path = os.path.join(projects_base_path, org_name)
                shutil.rmtree(project_path)
                print(f"{BOLD_GREEN}Deleted project '{org_name}'.")
                return projects_base_path
            else:
                print(f"{BOLD_YELLOW}Project deletion cancelled.")
        else:
            print(f"{BOLD_RED}Invalid project number.")
    else:
        print(f"{BOLD_RED}Please enter a valid number.")
    return None


def list_projects():
    clear_screen()
    projects = [d for d in os.listdir(projects_base_path) if os.path.isdir(os.path.join(projects_base_path, d))]
    return projects


def project_submenu():
    clear_screen()
    project_path = None
    while True:
        print(f"\n{BOLD_GREEN}Project Management Menu:\n")
        print(f"{BOLD_GREEN}1. Create Project")
        print(f"{BOLD_GREEN}2. Load Project")
        print(f"{BOLD_GREEN}3. Delete Project")

        print(f"\n{BOLD_CYAN}Utilities:")
        print(f"{BOLD_RED}X. Return to Main Menu")

        choice = input("\nEnter your choice: ").strip().lower()

        if choice == '1':
            clear_screen()
            org_name = input(f"{BOLD_GREEN}Enter the organization name for the new project: ").strip()
            project_path = create_project_directory(org_name)
            save_last_project(org_name)
            if project_path:
                os.chdir(project_path)
        elif choice == '2':
            clear_screen()
            project_path = load_project()
            save_last_project(os.path.basename(project_path))
            if project_path:
                os.chdir(project_path)
        elif choice == '3':
            clear_screen()
            project_path = delete_project()
            if project_path:
                os.chdir(project_path)
        elif choice == 'x':
            print(f"{BOLD_YELLOW}Returning to the main menu...")
            break
        else:
            print(f"{BOLD_RED}Invalid choice, please try again.")

    return project_path or projects_base_path


if __name__ == "__main__":
    project_submenu()
