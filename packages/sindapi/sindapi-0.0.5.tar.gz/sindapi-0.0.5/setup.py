import setuptools

setuptools.setup(
    name="sindapi",
    version="0.0.5",
    author="Helios1208",
    author_email="cly020329@gmail.com",
    description="api for SinD dataset",
    packages=setuptools.find_packages(),
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
    install_requires=['numpy', 'pyyaml', ],
)