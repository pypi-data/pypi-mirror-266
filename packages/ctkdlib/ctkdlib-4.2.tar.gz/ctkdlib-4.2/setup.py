from setuptools import setup

def get_long_description(path):
    """Opens and fetches text of long descrition file."""
    with open(path, 'r') as f:
        text = f.read()
    return text

setup(
    name = 'ctkdlib',
    version = '4.2',
    description = "A special widget library for CTkDesigner",
    license = "MIT",
    readme = "README.md",
    long_description = get_long_description('README.md'),
    long_description_content_type = "text/markdown",
    author = 'Akash Bora',
    url = "https://github.com/Akascape/CTkDesigner",
    package_data = {'': ['*.png']},
    classifiers = [
        "License :: OSI Approved :: MIT License ",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    keywords = ['customtkinter', 'tkinter', 'ctkdesigner', 'gui-builder', 'ui-designer', 'python-gui-builder'],
    packages = ["ctkdlib", "ctkdlib.custom_widgets"],
    install_requires = ['customtkinter', 'pillow'],
    dependency_links = ['https://pypi.org/project/customtkinter/', 'https://pypi.org/project/pillow/'],
    python_requires = '>=3.6',
)
