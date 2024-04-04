
import pathlib
import setuptools
setuptools.setup(
    name="Group9",
    version="0.1.0",
    description="Brief description",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Elen Sukiasyan",
    license="The Unlicense",
    classifiers=[
        "Development Status :: 3 - Alpha"
    ],
    python_requires=">=3.10, <3.12", 
    install_requires=["requests", "pandas>=2.0"]
)
