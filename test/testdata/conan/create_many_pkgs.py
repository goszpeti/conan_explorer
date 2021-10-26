import os
import pathlib
os.chdir(pathlib.Path(__file__).parent)

# create many packages to generate load on the get local packages function

for i in range(0, 400):
    os.system(f"conan create . example{i}/1.0.0@local/spam")