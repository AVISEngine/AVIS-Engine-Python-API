from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="avisengine",
    version="0.1.3",
    author="Amirmohammad Zarif",
    author_email="amirmohammadzarif@avisengine.com",
    description="Python API for AVIS Engine Simulator - A robust simulation platform for autonomous vehicle development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AvisEngine/AVIS-Engine-Python-API",
    project_urls={
        "Homepage": "https://avisengine.com",
        "Documentation": "https://docs.avisengine.com",
        "Source": "https://github.com/AvisEngine/AVIS-Engine-Python-API",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.18.3",
        "opencv-contrib-python>=4.2.0.34",
        "opencv-python>=4.2.0.34",
        "Pillow>=7.1.2",
        "PySocks>=1.7.1",
        "PyYAML>=5.3.1",
        "regex>=2020.4.4",
        "requests>=2.22.0"
    ],
)
