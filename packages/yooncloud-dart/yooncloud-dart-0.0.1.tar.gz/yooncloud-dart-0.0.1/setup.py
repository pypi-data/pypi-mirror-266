from setuptools import setup, find_packages

setup(
    name='yooncloud-dart',
    version='0.0.1',
    install_requires=["numpy==1.26.4", "pandas==2.2.1", "urllib==2.2.1"],
    packages=find_packages(),
    python_requires='>=3.8',
)