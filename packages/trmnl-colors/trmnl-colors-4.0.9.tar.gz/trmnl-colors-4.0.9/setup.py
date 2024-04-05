import setuptools

with open("README.md", "r") as fh:
    description = fh.read()
# TODO: Increment the version number and release it.
setuptools.setup(
    name="trmnl-colors",
    version="4.0.9",
    author="Idris-Vohra",
    author_email="idrishaider987@gmail.com",
    packages=["trmnl_colors"],
    description="Colors, text formats, decorations and much more for TERMINAL",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/Idrisvohra9/colors",
    license='MIT',
    python_requires='>=3.8',
    install_requires=[]
)
