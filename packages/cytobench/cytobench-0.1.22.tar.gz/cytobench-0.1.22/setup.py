from setuptools import setup, find_packages

setup(
    name='cytobench',
    version='0.1.21',
    packages=find_packages(),
    install_requires=[
        'numpy==1.23.5',
        'pandas==1.5.3',
        'scipy==1.11.4',
        'scikit-learn==1.2.2',
        'requests',
        'mega.py',
    ],
    author="Nicolo' Lazzaro",
    author_email='nlazzaro@fbk.eu',
    description='Benchmarking library for generative algorithms in omics data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/username/package_name',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)