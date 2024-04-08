# Copyright (c) 2023-2023 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages  # type: ignore
from distutils.command.install import install

with open('requirements.txt', encoding='utf-8') as f:
    required = f.read().splitlines()


class convert_install(install):
    def run(self):
        super().run()
        import os
        from subprocess import call

        call(os.path.join(os.path.dirname(os.path.realpath(__file__)), "convert_scripts", "build.sh"))


setup(
    name='convert_tool',
    cmdclass={"install": convert_install},
    version='7.0.0a1',
    description='model convert tool',
    url='https://gitee.com/ascend/ait',
    packages=find_packages(),
    license='Apache-2.0',
    keywords='convert tool',
    install_requires=required,
    classifiers=[
        'Development Status :: Alpha',
        'Intended Audience :: Developers',
        'License :: Apache-2.0 Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
    ],
    python_requires='>=3.7',
    entry_points={
        'convert_sub_task': ['convert=model_convert.__main__:get_cmd_instance'],
        'console_scripts': ['ait-build-aie=model_convert.__main__:build_aie'],
    },
)
