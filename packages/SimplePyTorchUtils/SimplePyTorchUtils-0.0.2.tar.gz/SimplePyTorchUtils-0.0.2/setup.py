from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    version="0.0.2",
    name="SimplePyTorchUtils",
    description="A collection of simple tools for working with PyTorch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gr1336/SimplePyTorchUtils/",
    install_requires=["torch>=2.0.0", "numpy"],
    author="gr1336",
    license=" Apache Software License",
    classifiers=[
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
)
