from setuptools import setup, find_packages

setup(
    name='flort',
    version='0.1.2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'flort = flort.__main__:main'
        ]
    },
    install_requires=[
        # Add any dependencies here
    ],
    author='Chris Watkins',
    author_email='chris@watkinslabs.com',
    description='A utilty to flatten your source code directory into a single file for LLM usage',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/chris17453/flort',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
)
