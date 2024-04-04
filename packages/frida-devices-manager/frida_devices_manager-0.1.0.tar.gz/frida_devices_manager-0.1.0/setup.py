import setuptools

import frida_devices_manager

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=frida_devices_manager.name,
    version=frida_devices_manager.__version__,
    author="369",
    author_email="luck.yangbo@gmail.com",
    description="A simple frida devices manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
