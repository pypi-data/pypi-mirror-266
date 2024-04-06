import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "opensearch-rest-resources",
    "version": "0.0.8",
    "description": "Manage OpenSearch REST resources from AWS CDK.",
    "license": "MIT",
    "url": "https://github.com/tmokmss/opensearch-rest-resources.git",
    "long_description_content_type": "text/markdown",
    "author": "tmokmss<tomookam@live.jp>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/tmokmss/opensearch-rest-resources.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "opensearch_rest_resources",
        "opensearch_rest_resources._jsii"
    ],
    "package_data": {
        "opensearch_rest_resources._jsii": [
            "opensearch-rest-resources@0.0.8.jsii.tgz"
        ],
        "opensearch_rest_resources": [
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
