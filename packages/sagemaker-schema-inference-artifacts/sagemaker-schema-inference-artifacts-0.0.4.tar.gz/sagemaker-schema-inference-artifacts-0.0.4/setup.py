# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""SageMaker Schema Inference Artifacts"""
from __future__ import absolute_import

import os
import subprocess
from glob import glob

from setuptools import find_packages, setup
from distutils.command.build import build


def npm_install(packages: dict[str, str]):
    """
    Installs node NPM package in the target destination (or in project root if the destination is not specified).
    """
    for package, destination in packages.items():
        cmd = f"npm install {package}"
        if destination is not None:
            target_dir = os.path.join(os.path.dirname(__file__), "src", "sagemaker_schema_inference_artifacts",
                                      destination)
            cmd = f"npm install --prefix {target_dir} {package}"
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def read(fname):
    """
    Args:
        fname:
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def read_version():
    return read("VERSION").strip()


def read_requirements(filename):
    """Reads requirements file which lists package dependencies.

    Args:
        filename: type(str) Relative file path of requirements.txt file

    Returns:
        list of dependencies extracted from file
    """
    with open(os.path.abspath(filename)) as fp:
        deps = [line.strip() for line in fp.readlines()]
    return deps


# NPM packages and respective destination targets
hugging_face_dir = "huggingface"
hugging_face_npm_dependencies = {
    '@huggingface/tasks@">=0.3.0"': hugging_face_dir,
}
npm_install(hugging_face_npm_dependencies)

extras = {
    "test": read_requirements("requirements/extras/test_requirements.txt")
}

install_requires = [
    "json5>=0.9.22",
]


class NPMInstall(build):
    def run(self):
        npm_install(hugging_face_npm_dependencies)
        build.run(self)


setup(
    name="sagemaker-schema-inference-artifacts",
    version=read_version(),
    description="Open source library for Hugging Face Task Sample Inputs and Outputs",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"": ["*.whl"]},
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    long_description=read("README.rst"),
    author="Amazon Web Services",
    url="https://github.com/aws/sagemaker-schema-inference-artifacts/",
    license="Apache License 2.0",
    keywords="ML Amazon AWS AI Schema Inference Artifacts",
    python_requires=">= 3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    extras_require=extras,
    install_requires=install_requires,
    cmdclass={
        'npm_install': NPMInstall
    },
)
