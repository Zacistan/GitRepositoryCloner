# GitRepositoryCloner
This script is a tool to clone all files from one Git Repository to a different Git Repository.  This is very useful if you want to easily and regularly clone from, for example, GitHub and push to GitLab.

## Use
1. Edit the 'config.json' with your Source Repository URL (where you will copy from) and your Destination Repository URL (where you will copy to)
2. Run this command in CMD or a shell:
```shell
python CloneToDestination.py
```

## Requirements
Ensure these are installed on your system:
* Python 3 (The script only needs the standard library)
* Git
