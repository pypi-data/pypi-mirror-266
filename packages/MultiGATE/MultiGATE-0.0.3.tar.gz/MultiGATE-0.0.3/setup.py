from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="MultiGATE",
    version="0.0.3",
    description="MultiGATE single cell",
    package_dir={"": "MultiGATE"},
    packages=find_packages(where="MultiGATE"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aqlkzf/MultiGATEtest1",
    author="Jinzhao LI & Jishuai MIAO",
    author_email="jishuaimiao@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
   install_requires=[
    'tensorflow-gpu==1.15.0',
    'scikit-learn',
    'pandas',
    'scanpy',
    'jupyterlab',
    'tqdm',
    'matplotlib',
    'networkx',
    'pybedtools',
    'seaborn',
    'scanpy'    
],

    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires="==3.7.*",
)