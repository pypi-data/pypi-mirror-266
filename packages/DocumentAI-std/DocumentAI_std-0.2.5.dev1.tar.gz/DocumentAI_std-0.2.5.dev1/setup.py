from setuptools import setup, find_packages

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="DocumentAI_std",
    version="0.2.5.dev1",
    # packages=find_packages(where='DocumentAI_std'),  # Include all packages within this directory
    packages=find_packages(exclude=["DocumentAI_std.tests"]),
    # package_dir={'': 'DocumentAI_std'},  # Set root package directory
    install_requires=required,
    url="",
    license="",
    author="Hamza Gbada",
    author_email="",
    description="The main standards for Latis Document AI project",
)
# TODO: about tesseract: https://stackoverflow.com/questions/63048908/how-do-i-install-a-new-language-pack-for-tesseract-on-windows