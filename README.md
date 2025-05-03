#### (for Mac) Common terminal commands:
```
- cd xyz: change into directory "xyz"
- cd ..: go back to parent directory
- pwd: check what your current directory is
```

# Download project
```
cd [the directory you want to clone the project folder in]
git clone ----
cd research-paper-finder
```
# Environment set up 
```
conda create -n research-paper-finder python=3.10
conda activate research-paper-finder
cd research-paper-finder
pip install requirements.txt
```
If you are using PyCharm, I suggest adding this env into this project by:

Click the menu bar: PyCharm --> Settings --> Python Interpreter --> Add Interpreter --> Add Local Interpreter --> Conda Environment --> Use existing environment --> choose "research-paper-finder" --> OK --> Apply 

# Deactivate environment
```
conda deactivate
```

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


