from setuptools import find_packages, setup


def read_requirements():
    with open('requirements.txt') as req:
        content = req.read()
        requirements = content.split('\n')
    return requirements


setup(
    name='qa_test',
    version='0.0.1',
    packages=find_packages(),
    package_data={
        'qwen_agent': ['*.tiktoken', '*.ttf'],
    },
    install_requires=read_requirements(),
    url='https://github.com/QwenLM/Qwen-Agent'
)
