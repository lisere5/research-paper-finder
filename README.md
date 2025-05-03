# Research Paper Finder – Setup & Git Guide

## 📚 Table of Contents
- [Common Terminal Commands (Mac)](#common-terminal-commands-mac)
- [Download Project](#download-project)
- [Environment Setup](#environment-set-up)
- [Setting up the Project in PyCharm](#opening-the-project-if-youre-using-pycharm)
- [Using Git](#using-git)
  - [Before You Start Editing](#before-you-start-editing)
  - [Pushing Your Code to GitHub](#pushing-your-code)
  - [Summary](#summary)
- [Running the Project](#to-run-open-terminal)
  - [Backend](#start-backend-server)
  - [Frontend](#start-frontend)

---

#### Common Terminal Commands (Mac)
```
- cd xyz: change into directory "xyz"
- cd ..: go back to parent directory
- pwd: check what your current directory is
```

# Download project
```
cd [the directory you want to clone the project folder in]
git clone git@github.com:lisere5/research-paper-finder.git
cd research-paper-finder
```
# Environment set up 
```
conda create -n research-paper-finder python=3.10
conda activate research-paper-finder
cd research-paper-finder
pip install requirements.txt
```

#### Deactivate environment
```
conda deactivate
```

# Opening the Project (if you're using PyCharm)

- Open --> select the project directory --> Trust

I suggest adding the conda env into this project by:

- Click the menu bar: PyCharm --> Settings --> Python Interpreter --> Add Interpreter --> Add Local Interpreter --> Conda Environment --> Use existing environment --> choose "research-paper-finder" --> OK --> Apply 

# Using Git
## Before you start editing:
### Get the most updated code by using this command
```
get checkout main
git pull origin main
```
### Then create and switch to your personal branch of code

**REPLACE `branchname` WITH YOUR NAME**  
(my name is Serena, so my command would look like git checkout -b serena-branch)
```
git checkout -b branchname
```
After creating the branch, in the future you don't need the -b, you can just say
```
git checkout branchname
```
A branch in Git is like a safe workspace where you can make changes to your code without affecting the main version. 
This is especially useful when working in teams, so each person can work on their own branch without interfering with others.

***DO NOT EDIT ANY CODE WHEN YOU ARE IN THE MAIN BRANCH, only edit it on your personal branch***


## Pushing Your Code
#### If you think your code is ready & you want to push to the remote repository on Github, follow the follwing steps
***AGAIN, MAKE SURE YOU ARE ON YOUR PERSONAL BRANCH***

- you can check what branch you are on with:
```
git branch
```
- To check what files you edited:
```
git status
```
- To add a single changed file (replace filename with the file you want to stage):
  - If I changed the file backend/main.py, I would write "git add backend/main.py"
```
git add filename
```
- To add all the files you changed (not recommended, adding the files one by one is better):
```
git add .
```
- To commit your changes:
  - If I added RAG functionality, the command might look like "git commit -m "added rag" "
```
git commit -m "explanation of what was changed"
```
- Then, pull again from the remote repository (as someone else might have pushed new code)
```
git merge main
```
- Lastly, push to the remote repository (replace branchname with your branchname!!)
```
git push -u origin branchname
```
### SUMMARY:
the pipeline to push to Github is:
check status of files --> add the changed files --> commit them w/ a msg description --> pull again --> push
### IMPORTANT!!! DO NOT PUSH TO MAIN!!!

# To run (open terminal)
#### Start backend server:
```
cd /backend
uvicorn main:app --reload
```
#### Exit backend server:
```
control + c
```
#### Start frontend:
```
command + t
conda activate research-paper-finder
cd ../frontend
streamlit run app.py
```
#### Stop frontend:
```
control + c
```


