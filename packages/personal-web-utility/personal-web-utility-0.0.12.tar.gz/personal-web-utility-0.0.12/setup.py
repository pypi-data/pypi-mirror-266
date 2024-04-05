import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="personal-web-utility",
    version="0.0.12",
    author="Mihael Macuka",
    author_email="mihaelmacuka2@gmail.com",
    description="Personal web application utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/mihael97/web-utility",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
