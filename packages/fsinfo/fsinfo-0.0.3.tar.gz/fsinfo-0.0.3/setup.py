from setuptools import setup, find_packages

setup(
    name='fsinfo',
    version='0.0.3',
    author='Karel Tutsu',
    author_email='karel.tutsu@gmail.com',
    description='A Python library for cross-platform filesystem operations, providing classes for handling files and directories.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/KarelOmab/fsinfo',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
