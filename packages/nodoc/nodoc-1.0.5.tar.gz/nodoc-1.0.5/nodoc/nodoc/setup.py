from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="nodoc",
    version="1.0.2",
    author="HangBack",
    author_email="3402977740@qq.com",
    description="Layer-by-layer manipulation of document data with ease and efficiency.",

    # 项目主页
    url="https://github.com/HangBack/nodoc",

    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(),

    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # 开发的目标用户
        'Intended Audience :: Developers',

        # 属于什么类型
        'Topic :: Software Development :: Build Tools',

        # 许可证信息
        'License :: OSI Approved :: MIT License',

        # 目标 Python 版本
        'Programming Language :: Python :: 3.11'
    ],
    install_requires=[
        'click==8.1.7',
        'faiss-cpu==1.7.4',
        'fsspec==2023.12.2',
        'huggingface-hub==0.19.4',
        'joblib==1.3.2',
        'nltk==3.8.1',
        'numpy==1.26.2',
        'packaging==23.2',
        'pandas==2.1.4',
        'Pillow',
        'psutil==5.9.6',
        'python-dateutil==2.8.2',
        'pytz==2023.3.post1',
        'regex==2023.10.3',
        'safetensors==0.4.1',
        'scikit-learn==1.3.2',
        'scipy==1.11.4',
        'sentence-transformers==2.2.2',
        'sentencepiece==0.1.99',
        'six==1.16.0',
        'threadpoolctl==3.2.0',
        'tokenizers==0.15.0',
        'torch==2.1.1',
        'torchaudio==2.1.1',
        'torchvision==0.16.1',
        'tqdm==4.66.1',
        'transformers==4.36.1',
        'triton==2.1.0',
        'tzdata==2023.3'
    ],
    python_requires = ">=3.11, <3.12",
    long_description=long_description
)
