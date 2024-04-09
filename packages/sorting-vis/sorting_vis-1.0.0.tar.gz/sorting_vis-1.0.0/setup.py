from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="sorting_vis",
    version="1.0.0",
    author="Tomas Vana",
    url="https://github.com/tomasvana10/sorting_vis",
    description="Visualise how different sorting algorithms manage an array.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    license="MIT",
    platforms="any",
    include_package_data=True,
    install_requires=[
        "customtkinter",
        "pillow"
    ],
    entry_points={
        "gui_scripts": [
            "sorting-ctk = sorting_vis.main:start",
        ],
    },
    classifiers=[
        "Topic :: Multimedia",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Education"
    ]
)