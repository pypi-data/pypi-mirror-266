import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "reapit-cdk.wildcard-certificate",
    "version": "0.1.0",
    "description": "This construct returns a wildcard certificate valid for subdomains of the given domain names, creating and validating on if it doesn't exist. It supports cross-account DNS validation, you can pass in arns of roles from other accounts and it'll assume them whilst doing the Route53 updates.",
    "license": "MIT",
    "url": "https://github.com/reapit/ts-cdk-constructs/blob/main/packages/constructs/wildcard-certificate",
    "long_description_content_type": "text/markdown",
    "author": "Josh Balfour<jbalfour@reapit.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/reapit/ts-cdk-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "reapit_cdk.wildcard_certificate",
        "reapit_cdk.wildcard_certificate._jsii"
    ],
    "package_data": {
        "reapit_cdk.wildcard_certificate._jsii": [
            "wildcard-certificate@0.1.0.jsii.tgz"
        ],
        "reapit_cdk.wildcard_certificate": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.96.2, <3.0.0",
        "constructs>=10.2.70, <11.0.0",
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
