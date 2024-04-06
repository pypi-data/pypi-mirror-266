import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "reapit-cdk.active-ruleset",
    "version": "0.1.2",
    "description": "This construct returns the currently active SES receipt RuleSet, or creates one. This enables you to add rules to it.",
    "license": "MIT",
    "url": "https://github.com/reapit/ts-cdk-constructs/blob/main/packages/constructs/active-ruleset",
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
        "reapit_cdk.active_ruleset",
        "reapit_cdk.active_ruleset._jsii"
    ],
    "package_data": {
        "reapit_cdk.active_ruleset._jsii": [
            "active-ruleset@0.1.2.jsii.tgz"
        ],
        "reapit_cdk.active_ruleset": [
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
