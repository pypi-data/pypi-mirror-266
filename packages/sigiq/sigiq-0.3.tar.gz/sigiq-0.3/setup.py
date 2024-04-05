from setuptools import setup, find_packages


setup(
    name='sigiq',
    version='0.3',
    packages=find_packages(),
    install_requires=[
        'requests',
        'openai',
        'llama-index-core==0.10.15',
    ],
)
