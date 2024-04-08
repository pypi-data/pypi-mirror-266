import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws_pdk",
    "version": "0.23.30",
    "description": "@aws/pdk",
    "license": "Apache-2.0",
    "url": "https://github.com/aws/aws-pdk",
    "long_description_content_type": "text/markdown",
    "author": "AWS APJ COPE<apj-cope@amazon.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/aws/aws-pdk"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_pdk",
        "aws_pdk._jsii",
        "aws_pdk.aws_arch",
        "aws_pdk.aws_arch.aws_arch",
        "aws_pdk.aws_arch.aws_arch.drawio_spec",
        "aws_pdk.aws_arch.aws_arch.drawio_spec.aws4",
        "aws_pdk.aws_arch.aws_arch.pricing_manifest",
        "aws_pdk.cdk_graph",
        "aws_pdk.cdk_graph_plugin_diagram",
        "aws_pdk.cdk_graph_plugin_threat_composer",
        "aws_pdk.cloudscape_react_ts_website",
        "aws_pdk.identity",
        "aws_pdk.infrastructure",
        "aws_pdk.monorepo",
        "aws_pdk.monorepo.nx",
        "aws_pdk.monorepo.syncpack",
        "aws_pdk.monorepo.syncpack.base_group_config",
        "aws_pdk.monorepo.syncpack.custom_type_config",
        "aws_pdk.monorepo.syncpack.semver_group_config",
        "aws_pdk.monorepo.syncpack.version_group_config",
        "aws_pdk.pdk_nag",
        "aws_pdk.pipeline",
        "aws_pdk.static_website",
        "aws_pdk.type_safe_api"
    ],
    "package_data": {
        "aws_pdk._jsii": [
            "pdk@0.23.30.jsii.tgz"
        ],
        "aws_pdk": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.7",
    "install_requires": [
        "aws-cdk-lib>=2.104.0, <3.0.0",
        "aws-cdk.aws-cognito-identitypool-alpha>=2.104.0.a0, <3.0.0",
        "cdk-nag>=2.28.2, <3.0.0",
        "constructs>=10.3.0, <11.0.0",
        "jsii>=1.91.0, <2.0.0",
        "projen>=0.79.24, <0.80.0",
        "publication>=0.0.3",
        "typeguard~=2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": [
        "src/aws_pdk/_jsii/bin/monorepo.nx-dir-hasher",
        "src/aws_pdk/_jsii/bin/monorepo.pnpm-link-bundled-transitive-deps",
        "src/aws_pdk/_jsii/bin/pdk",
        "src/aws_pdk/_jsii/bin/type-safe-api.clean-openapi-generated-code",
        "src/aws_pdk/_jsii/bin/type-safe-api.copy-async-smithy-transformer",
        "src/aws_pdk/_jsii/bin/type-safe-api.copy-gradle-wrapper",
        "src/aws_pdk/_jsii/bin/type-safe-api.generate",
        "src/aws_pdk/_jsii/bin/type-safe-api.generate-html-redoc-docs",
        "src/aws_pdk/_jsii/bin/type-safe-api.generate-mock-data",
        "src/aws_pdk/_jsii/bin/type-safe-api.parse-openapi-spec"
    ]
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
