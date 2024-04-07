from setuptools import setup, find_packages

setup(
    name='CINOSUM',
    version='1.0.5',
    description='Chinese Minority Extractive Multi-language summarization project',
    author='HaoYu Luo',
    author_email='506685820@qq.com',
    packages=find_packages(),
    install_requires=[
        'torch',
        'numpy',
        'tqdm',
        'transformers==4.33.1',
    ],
    
    
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)