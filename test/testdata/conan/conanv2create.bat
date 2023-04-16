conan remote add local  http://localhost:9300/v2
conan create conanfileV2.py --version 1.0.0 -pr .\profile\windowsV2
conan create conanfileV2.py --version 1.0.0 -pr .\profile\linuxV2

conan upload example/1.0.0 -r local --force
conan install --requires example/1.0.0 -pr .\profile\windowsV2