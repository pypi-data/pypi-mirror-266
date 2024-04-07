from setuptools import setup, find_packages

# 读取README.md文件内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='CINOSUM',
    version='1.0.6',
    description='Chinese Minority Extractive Multi-language summarization project',
    long_description=long_description,  # 将README内容作为long_description
    long_description_content_type="text/markdown",  # 指定long_description的格式为markdown
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