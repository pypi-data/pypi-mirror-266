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

import os

from setuptools import setup, find_packages


abs_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(abs_path, "requirements.txt")) as f:
    required = f.read().splitlines()

extras_requires = {
    'aclruntime': [
        'aclruntime @ git+https://gitee.com/ascend/ait.git#egg=aclruntime&subdirectory=ait/components/benchmark/backend'
    ],
    'benchmark': [
        'ais_bench @ git+https://gitee.com/ascend/ait.git#egg=ais_bench&subdirectory=ait/components/benchmark'
    ],
    'surgeon': [
        'auto_optimizer @ git+https://gitee.com/ascend/ait.git#egg=auto_optimizer&subdirectory=ait/components/debug/surgeon'
    ],
    'compare': [
        'compare @ git+https://gitee.com/ascend/ait.git#egg=compare&subdirectory=ait/components/debug/compare'
    ],
    'analyze': [
        'analyze_tool @ git+https://gitee.com/ascend/ait.git#egg=analyze_tool&subdirectory=ait/components/analyze'
    ],
    'transplt': [
        'transplt @ git+https://gitee.com/ascend/ait.git#egg=transplt&subdirectory=ait/components/transplt'
    ],
    'convert': [
        'convert_tool @ git+https://gitee.com/ascend/ait.git#egg=convert_tool&subdirectory=ait/components/convert'
    ],
    'profile': [
        'msprof @ git+https://gitee.com/ascend/ait.git#egg=msprof&subdirectory=ait/components/profile/msprof'
    ],
    'llm': [
        'ait-llm @ git+https://gitee.com/ascend/ait.git#egg=ait-llm&subdirectory=ait/components/llm'
    ],
}

extras_requires['full'] = list(
    set(url for _, rqs in extras_requires.items() for url in rqs)
)

setup(
    name='ms-ait',
    version='7.0.0a4',
    description='AIT, Ascend Inference Tools',
    long_description_content_type='text/markdown',
    url='https://gitee.com/ascend/ait',
    packages=find_packages(),
    package_data={
        '': ['LICENSE', 'requirements.txt'],
        'ms-ait': ['LICENSE', 'requirements.txt'],
    },
    data_files=[
        ('', ['requirements.txt']),
    ],
    license='Apache-2.0',
    keywords='ait',
    python_requires='>=3.7',
    install_requires=required,
    extras_require={'full': ["ait-surgeon==0.1.1"]},
    entry_points={
        'console_scripts': ['ait=components.__main__:main'],
    },
)
