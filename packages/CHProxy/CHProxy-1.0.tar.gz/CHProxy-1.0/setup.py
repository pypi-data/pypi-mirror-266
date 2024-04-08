from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='CHProxy',
    version='1.0',
    description='Get long-term proxy from caihongdaili.com',
    long_description=long_description,
    author='369',
    author_email='luck.yangbo@gmail.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
