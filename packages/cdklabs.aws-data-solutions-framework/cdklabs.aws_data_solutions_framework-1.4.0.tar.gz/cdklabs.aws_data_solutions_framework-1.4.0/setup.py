import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdklabs.aws_data_solutions_framework",
    "version": "1.4.0",
    "description": "L3 CDK Constructs used to build data solutions with AWS",
    "license": "Apache-2.0",
    "url": "https://awslabs.github.io/data-solutions-framework-on-aws/",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/awslabs/data-solutions-framework-on-aws.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdklabs.aws_data_solutions_framework",
        "cdklabs.aws_data_solutions_framework._jsii",
        "cdklabs.aws_data_solutions_framework.consumption",
        "cdklabs.aws_data_solutions_framework.governance",
        "cdklabs.aws_data_solutions_framework.processing",
        "cdklabs.aws_data_solutions_framework.storage",
        "cdklabs.aws_data_solutions_framework.utils"
    ],
    "package_data": {
        "cdklabs.aws_data_solutions_framework._jsii": [
            "aws-data-solutions-framework@1.4.0.jsii.tgz"
        ],
        "cdklabs.aws_data_solutions_framework": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.114.1, <3.0.0",
        "aws-cdk.lambda-layer-kubectl-v27>=2.1.0, <3.0.0",
        "constructs>=10.3.0, <11.0.0",
        "jsii>=1.95.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
