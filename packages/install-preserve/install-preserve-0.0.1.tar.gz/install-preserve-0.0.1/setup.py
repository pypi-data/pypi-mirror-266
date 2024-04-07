from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='install-preserve',
    version='0.0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
        ],
    },
    author='Manbehindthemadness',
    author_email='manbehindthemadness@gmail.com',
    description='A Python library that helps prevent accidental overwrites of hand-compiled libraries',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/manbehindthemadness/install-preserve',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.0',
)
