import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="wen_evm_wallet",
    version="0.2",
    author="wuwen7075",
    author_email="",
    description="create evm wallet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/av11000000/wen_evm_wallet",
    packages=setuptools.find_packages(),
    install_requires=['eth_account==0.9.0'],
    entry_points={
        'console_scripts': [
            'eth-wallet=src:wallet'
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)