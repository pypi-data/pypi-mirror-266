from setuptools import setup, find_packages

setup(
    name="KANGROLL",
    version="0.1.0",
    author="Xiaowen Kang",
    author_email="kangxiaowen@Gmail.com",
    description="KANGROLL to buid a bridge between science and nature",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/williampolicy/kangroll",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
