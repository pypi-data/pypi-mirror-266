import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-use-cases.custom-cloud9-ssm",
    "version": "1.3.1",
    "description": "Pattern for Cloud9 EC2 environment and SSM Document.",
    "license": "Apache-2.0",
    "url": "https://github.com/aws-samples/cdk-use-cases.git",
    "long_description_content_type": "text/markdown",
    "author": "Borja Pérez Guasch",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws-samples/cdk-use-cases.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_use_cases.custom_cloud9_ssm",
        "cdk_use_cases.custom_cloud9_ssm._jsii"
    ],
    "package_data": {
        "cdk_use_cases.custom_cloud9_ssm._jsii": [
            "custom-cloud9-ssm@1.3.1.jsii.tgz"
        ],
        "cdk_use_cases.custom_cloud9_ssm": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.135.0, <3.0.0",
        "constructs>=10.3.0, <11.0.0",
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
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": [
        "src/cdk_use_cases/custom_cloud9_ssm/_jsii/bin/custom-cloud9-ssm"
    ]
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
