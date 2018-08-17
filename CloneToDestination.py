import os, shutil
import json
import time
import sys
from subprocess import check_call, call

def rmtree_onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    if not os.access(path, os.W_OK):
        # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def initialize_workspace(repo_folder_1, repo_folder_2, disable_git_ssl):
    """
    Creates folders necessary to clone source and destination 
    repos.

    Also disables Git's SSL verification if the flag is set 
    (Useful if using internal Certificate Authority)
    """
    if not os.path.exists(repo_folder_1):
        os.makedirs(repo_folder_1)

    if not os.path.exists(repo_folder_2):
        os.makedirs(repo_folder_2)

    if disable_git_ssl == 'true':
        os.environ['GIT_SSL_NO_VERIFY'] = 'true'


def push_to_destination(source_repository, destination_repository, configuration):
    """
    Takes source repository and pushes the files to the 
    destination repository.

    1. Clones both repositories. 
    2. Deletes the .git folder from the source directory.
    3. Copies the .git folder of the destination directory to 
       the source directory 
    4. Stage, commit, and push all changes in the source 
       directory to the destination repository
    """
    # Variables
    source_repo_git_folder = os.path.join(source_repository, '.git/')
    destination_repo_git_folder = os.path.join(destination_repository, '.git/')

    # Shell commands
    clone_source_repo_command = 'git clone {0} {1}'.format(configuration['source_repository_url'], source_repository)
    clone_destination_repo_command = 'git clone {0} {1}'.format(configuration['destination_repository_url'], destination_repository)
    stage_changes = 'cd {0} & git add -A'.format(source_repository)
    commit_changes = 'cd {0} & git commit -m "Cloned changes from remote repository at {1}"'.format(source_repository, configuration['source_repository_url'])
    push_changes = 'cd {0} & git push'.format(source_repository)

    # Clone the two repos
    try:
        check_call(clone_source_repo_command)
    except:
        print("Error attempting to clone from source repo. Check connection to Git server.")
        raise

    try:
        check_call(clone_destination_repo_command)
    except:
        print("Error attempting to clone from destination repo. Check connection to Git server.")
        raise

    # Delete git folder from source repo; copy in git folder from destination repository
    shutil.rmtree(os.path.abspath(source_repo_git_folder), onerror=rmtree_onerror)
    shutil.copytree(destination_repo_git_folder, source_repo_git_folder)

    # Run Git commands to push to destination repository
    call(stage_changes, shell=True)
    call(commit_changes, shell=True)
    call(push_changes, shell=True)

def delete_workspace(repo_folder_1, repo_folder_2):
    """
    Deletes folders used to clone repositories
    """
    time.sleep(5) # Sometimes Git takes a second to unlock all files
    if os.path.exists(repo_folder_1):
        shutil.rmtree(repo_folder_1, onerror=rmtree_onerror)

    if os.path.exists(repo_folder_2):
        shutil.rmtree(repo_folder_2, onerror=rmtree_onerror)


def __main__():
    with open('config.json') as conf:
        config = json.load(conf)

    basedir = os.path.dirname(__file__)
    source_repo_folder = os.path.join(basedir, 'source_cloned/')
    destination_repo_folder = os.path.join(basedir, 'destination_cloned/')

    try:
        initialize_workspace(repo_folder_1=source_repo_folder, 
                             repo_folder_2=destination_repo_folder, 
                             disable_git_ssl=config['disable_git_ssl_verify'])
    except:
        print("Error attempting to create workspace. Check your permissions to the folder the script is located in.")
        raise

    try:
        push_to_destination(source_repository=source_repo_folder, 
                            destination_repository=destination_repo_folder, 
                            configuration=config)
    except:
        raise
    finally:
        try:
            delete_workspace(repo_folder_1=source_repo_folder, 
                             repo_folder_2=destination_repo_folder)
        except:
            print("Error attempting to delete workspace. Check your permissions to the folder the script is located in.")
            raise

__main__()