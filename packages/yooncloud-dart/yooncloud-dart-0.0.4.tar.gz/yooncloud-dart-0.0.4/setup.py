from setuptools import setup, find_packages

setup(
    name='yooncloud-dart',
    version='0.0.4',
    install_requires=["numpy==1.26.4", "pandas==2.2.1", "arelle-release"],
    packages=find_packages(),
    python_requires='>=3.8',
)