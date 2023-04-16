import os
import pathlib
os.chdir(pathlib.Path(__file__).parent)

# create many packages to generate load on the get local packages function

# for i in range(0, 20):
#     os.system(f"conan create . example{i}/{i+1}.{i+2}.0@local/spam")
#     os.system(f"conan upload example{i}/{i+1}.{i+2}.0@local/spam -r local")

for i in range(0, 20):
    os.system(f"conan create . manypackages{i}/{i}.{i+1}.0@local2/spam{i}")
    os.system(f"conan upload manypackages{i}/{i}.{i+2}.0@local2/spam{i} -r local")
