import os
import platform
import subprocess

import setuptools

PROJECT_SRC_DIR = os.path.abspath(os.path.join(os.getcwd(), "../../.."))
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROTO_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "clickzetta/proto/source"))
PROTO_OUT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "clickzetta/proto/generated"))

os.makedirs(PROTO_OUT_DIR, exist_ok=True)

for source_file in os.listdir(PROTO_DIR):
    subprocess.call(
        'python -m grpc_tools.protoc -I . --python_out=' + PROTO_OUT_DIR + ' --grpc_python_out=' + PROTO_OUT_DIR
        + ' --proto_path =' + PROTO_DIR + ' '
        + os.path.abspath(os.path.join(PROTO_DIR, source_file)), shell=True)

for generated_file in os.listdir(PROTO_OUT_DIR):
    if platform.system() == "Darwin":
        subprocess.call("sed -i '' 's/^import /from . import /' " + os.path.abspath(
            os.path.join(PROTO_OUT_DIR, generated_file)), shell=True)
    elif platform.system() == "Linux":
        subprocess.call("sed -i 's/^import /from . import /' " + os.path.abspath(
            os.path.join(PROTO_OUT_DIR, generated_file)), shell=True)

# Package metadata.

name = "clickzetta-connector"
description = "clickzetta python connector"

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = "Development Status :: 3 - Alpha"
dependencies = [
    "proto-plus >= 1.22.0, <2.0.0dev",
    "packaging >= 14.3, <24.0.0dev",
    "protobuf>=3.19.5,<5.0.0dev,!=3.20.0,!=3.20.1,!=4.21.0,!=4.21.1,!=4.21.2,!=4.21.3,!=4.21.4,!=4.21.5",
    "python-dateutil >= 2.7.2, <3.0dev",
    "requests >= 2.21.0, < 3.0.0dev",
    "pyarrow >= 10.0.1, <11.0.0",
    "sqlalchemy >= 1.4.0, <2.0.0",
    #"ossfs >= 2023.1.0",
    "cz-ossfs >= 0.0.2",
    "cos-python-sdk-v5 >= 1.9.25",
    "pandas >=1.5.3",
]

# Setup boilerplate below this line.

package_root = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(package_root, "clickzetta/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

packages = ['clickzetta', 'clickzetta.dbapi', 'clickzetta.bulkload', 'clickzetta.proto.generated']

setuptools.setup(
    name=name,
    version=version,
    description=description,
    url='https://www.zettadecision.com/',
    author="mocun",
    author_email="hanmiao.li@clickzetta.com",
    platforms="Posix; MacOS X;",
    packages=packages,
    install_requires=dependencies,
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
)
