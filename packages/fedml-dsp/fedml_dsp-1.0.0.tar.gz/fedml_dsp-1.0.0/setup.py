import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="fedml_dsp",
    version="1.0.0",
    author="SAP SE",
    description="A python library for building machine learning models on gpu AI Platforms using a federated data source",
    license='Apache License 2.0',
    license_files = ['LICENSE.txt'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "hdbcli", 'numpy==1.23.0', 'pandas<1.6.0dev0,>=1.3', 'pyspark', 'ai-core-sdk', 'pyyaml', 'requests', 'pyarrow<15', 'torch'
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3",
    include_package_data=True
)