import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "packyak-aws-cdk",
    "version": "0.4.26",
    "description": "AWS CDK Constructs for the PackYak Lakehouse Platform",
    "license": "Apache-2.0",
    "url": "https://github.com/sam-goodwin/packyak",
    "long_description_content_type": "text/markdown",
    "author": "Sam Goodwin",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/sam-goodwin/packyak"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "packyak_aws_cdk",
        "packyak_aws_cdk._jsii"
    ],
    "package_data": {
        "packyak_aws_cdk._jsii": [
            "aws-cdk@0.4.26.jsii.tgz"
        ],
        "packyak_aws_cdk": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib==2.134.0",
        "aws-cdk.aws-glue-alpha==2.134.0.a0",
        "aws-cdk.aws-lambda-python-alpha==2.134.0.a0",
        "aws-cdk.aws-sagemaker-alpha==2.134.0.a0",
        "constructs>=10.3.0, <11.0.0",
        "jsii>=1.94.0, <2.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved",
        "Framework :: AWS CDK",
        "Framework :: AWS CDK :: 1"
    ],
    "scripts": [
        "src/packyak_aws_cdk/_jsii/bin/packyak"
    ]
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
