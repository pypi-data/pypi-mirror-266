import setuptools

setuptools.setup(
    name="yosemite-tools",
    version="0.0.01",
    author="Hammad Saeed",
    author_email="hammad@supportvectors.com",
    description="yosemite",
    long_description="""
Yosemite
    """,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>3.8',
    install_requires=[
"art",
"prompt_toolkit",
"pathlib",
"rich-cli",
"rich",
    ],
)