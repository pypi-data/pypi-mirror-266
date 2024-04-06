import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-vpc-toumoro-projen",
    "version": "0.0.5",
    "description": "A CDK construct library to create a VPC with public and private subnets.",
    "license": "GPL-3.0-or-later",
    "url": "https://github.com/tm-lcarvalho/cdk-vpc-toumoro-projen.git",
    "long_description_content_type": "text/markdown",
    "author": "tm-lcarvalho<lucio.carvalho@toumoro.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/tm-lcarvalho/cdk-vpc-toumoro-projen.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk-vpc-toumoro-projen",
        "cdk-vpc-toumoro-projen._jsii"
    ],
    "package_data": {
        "cdk-vpc-toumoro-projen._jsii": [
            "cdk-vpn-toumoro-projen@0.0.5.jsii.tgz"
        ],
        "cdk-vpc-toumoro-projen": [
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
