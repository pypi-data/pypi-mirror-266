import setuptools
from os import path
this_directory = path.abspath(path.dirname(__file__))

install_deps = [
    'datetime',
    'tqdm',
    'fastremap',
    'scikit-learn==1.2.2',#==1.2.2
    'numpy==1.18.5',#1.18.5
    'scipy',
    'torch',#pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    'tifffile',
    'paramiko',
    'pillow==9.1',#9.1
    'PyQt5',
    'pyqt5-sip==12.12.2',
    'scikit-image==0.17.2',#0.17.2
    'opencv-python',
    'pyqtgraph==0.12.4',#==0.12.4
    'ruamel.yaml',
    'tensorflow==2.3.0',#2.3.0
    'keras==2.3.1',
    'natsort',
    'numba>=0.53.1',
    'matplotlib==3.5.0',#==3.5
    'protobuf==3.20.1',#==3.20.1
    'csaps',
]


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="neuroai",
    version="0.0.0",
    author="HuJiahao",
    author_email="dadadadasukede@gmail.com",
    description="A package for calcium image processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=" ",
    install_requires=install_deps,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.8'
)