from setuptools import (
    find_packages,
    setup,
)


# 从 requirements.txt 读取依赖
def parse_requirements(filename):
    line_iter = (line.strip() for line in open(filename))
    return [line for line in line_iter if line and not line.startswith("#")]


setup(
    name='hs_correct',
    version='0.0.3',
    description='hs-correct-module',
    classifiers=[],
    keywords='hs-correct-module',
    author='zgl',
    author_email='',
    url='',
    license='MIT',
    packages=find_packages(exclude=[]),
    package_data={'': ['*.*']},
    include_package_data=True,
    install_requires=parse_requirements('correct/requirements.txt'),
    long_description='hs alignment&correct module'
)
