from setuptools import setup, find_packages

setup(
    name='extensionizer',
    version='0.0.2',
    description='Python package to create chrome extensions quickly',
    long_description="""
Extensionizer is a Python package designed to streamline the process of creating Chrome extensions. With Manifest, you can quickly generate the necessary files, including the `manifest.json` file and the files required for the extension's popup interface, such as HTML, CSS, and JavaScript.

Features:
- Easily create and customize the `manifest.json` file for your Chrome extension.
- Generate popup interface files (HTML, CSS, and JavaScript) with minimal effort.
- Simple and intuitive API for defining permissions, background scripts, content scripts, and more.
- Compatible with Python 3.6 and above.

Getting Started:
1. Install extensionizer using `pip install extensionizer`.
2. Use the provided classes and methods to define your extension's properties and generate the required files.
3. Build and test your extension locally before publishing it to the Chrome Web Store.

Manifest is ideal for developers who want to automate the creation of Chrome extensions and focus on building innovative features without getting bogged down in repetitive setup tasks. Get started with Manifest today and supercharge your Chrome extension development workflow!
    """,
    author='Yash Sharma',
    author_email='yashsharmaat2004@gmail.com',
    url='https://github.com/Yash182023/Manifest',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
