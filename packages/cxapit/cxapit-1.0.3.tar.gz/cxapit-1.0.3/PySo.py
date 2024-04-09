import os
from distutils.core import setup
from Cython.Build import cythonize

main_path="./cxapit/"
main_name="cxapit"
setup(
    ext_modules = cythonize([
        # main_path+"Tools.py",
        # main_path+"Authentications.py",
        main_path+"base/tools/Common.py"]
        )
)

# os.system("mv "+main_path+"Tools.*.so "+main_path+"Tools.so")
# os.system("mv "+main_path+"Authentications.*.so "+main_path+"Authentications.so")
# os.system("mv "+main_path+"Common.*.so "+main_path+"base/tools/Common.so")
os.system("rm -rf build "+main_path+"*.c")
