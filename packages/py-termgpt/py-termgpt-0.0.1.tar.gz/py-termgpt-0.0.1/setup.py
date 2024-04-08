from setuptools import setup, find_packages

setup(
    name="termgpt",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'termgpt=termgpt.adder:main',
        ],
    },
    install_requires=[
        # List your project's dependencies here, e.g.,
        'requests',
    ],
)