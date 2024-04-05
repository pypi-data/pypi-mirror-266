import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "rantoniuk.cloudwatch-retention-setter",
    "version": "0.0.15",
    "description": "Based on EventBridge rule, automatically set the logGroup retention policy when new AWS CloudWatch logGroup is created.",
    "license": "Apache-2.0",
    "url": "https://github.com/rantoniuk/cloudwatch-retention-setter.git",
    "long_description_content_type": "text/markdown",
    "author": "Radek Antoniuk<radek.antoniuk@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/rantoniuk/cloudwatch-retention-setter.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "rantoniuk.cloudwatch_retention_setter",
        "rantoniuk.cloudwatch_retention_setter._jsii"
    ],
    "package_data": {
        "rantoniuk.cloudwatch_retention_setter._jsii": [
            "cloudwatch-retention-setter@0.0.15.jsii.tgz"
        ],
        "rantoniuk.cloudwatch_retention_setter": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.96.0, <2.0.0",
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
