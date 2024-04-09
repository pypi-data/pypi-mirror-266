from setuptools import find_packages, setup

with open("./README.md", "r") as f:
    long_description = f.read()

setup(
    name="demo_alphav2",
    version="2.0.1",
    description="A package of alphav2",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quandn2003/demo_package_alphav2",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    # install_requires=[
    #     'matplotlib==3.7.4',
    #     'numpy==1.23.5',
    #     'pandas==2.0.3',
    #     'Requests==2.31.0',
    #     'scikit_learn==1.3.2',
    #     'setuptools==69.0.3',
    #     'xgboost==2.0.3'
    # ],
    # extras_require={
    #     'dev': ['pytest', 'sphinx'],
    #     # 'gpu': ['cupy', 'tensorflow-gpu']
    # },
    python_requires=">=3.10",
)