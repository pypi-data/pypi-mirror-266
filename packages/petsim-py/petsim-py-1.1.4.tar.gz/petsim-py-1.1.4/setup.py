from setuptools import setup, find_packages

setup(
    name="petsim-py",
    version="1.1.4",
    author="YbicG.Database",
    author_email="contact@ybicg.com",
    description="Wrapper for the BIG Games API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YbicG/petsim-py",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=["requests"],
)
