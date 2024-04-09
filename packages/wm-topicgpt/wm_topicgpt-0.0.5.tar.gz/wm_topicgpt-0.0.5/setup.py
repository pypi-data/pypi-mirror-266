from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

setup(
    name='wm_topicgpt',
    version='0.0.5',
    description='This is a package to generate topics for the text corpus.',
    packages=find_packages(),
    install_requires=install_requires,
    python_requires='>=3.9',
)