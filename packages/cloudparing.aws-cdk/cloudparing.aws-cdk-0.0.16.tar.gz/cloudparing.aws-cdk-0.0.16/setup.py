import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cloudparing.aws-cdk",
    "version": "0.0.16",
    "description": "The cloudparing CDK library",
    "license": "Apache-2.0",
    "url": "https://github.com/cloudparing/cloudparing-cdk",
    "long_description_content_type": "text/markdown",
    "author": "James Ayvaz<james@cloudparing.net>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cloudparing/cloudparing-cdk"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cloudparing.aws_cdk",
        "cloudparing.aws_cdk._jsii"
    ],
    "package_data": {
        "cloudparing.aws_cdk._jsii": [
            "aws-cdk-lib@0.0.16.jsii.tgz"
        ],
        "cloudparing.aws_cdk": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.1.0, <3.0.0",
        "constructs>=10.3.0, <11.0.0",
        "jsii>=1.97.0, <2.0.0",
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
