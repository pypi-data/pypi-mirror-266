from distutils.core import setup

# Edit this to update the package version
VERSION = "0.0.8"

FULL_VERSION = VERSION.replace(".", "")

setup(
    name="fastclip",
    version=VERSION,
    license="MIT",
    description="A private library for fastclip",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Fastclip",
    author_email="hello+pip@fastclip.io",
    url="https://github.com/fastclip/library",
    download_url=f"https://github.com/fastclip/library/archive/v_{FULL_VERSION}.tar.gz",
    keywords=[
        "fastclip",
    ],
    install_requires=[
        "typing_extensions",
        "pydantic",
    ],
    packages=["fastclip", "fastclip.enums", "fastclip.schemas"],
)
