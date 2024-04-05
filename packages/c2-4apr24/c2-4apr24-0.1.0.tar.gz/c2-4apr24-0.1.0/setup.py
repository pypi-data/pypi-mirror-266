from setuptools import setup, find_packages

test_packages = ["pytest>=8.1.1"]
base_packages = [
    "transformers>=4.39",
    "datasets>=2.18",
    "scikit-learn>=1.3.2",
    "ruff>=0.3.4",
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="c2-4apr24",
    packages=find_packages(exclude=["notebooks", "docs"]),
    version="0.1.0",
    author="Sumanth S Prabhu",
    author_email="sumanthprabhu.104@gmail.com",
    description="Data Quality Check for Machine Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sumanthprabhu/C2",
    project_urls={
        "Source Code": "https://github.com/sumanthprabhu/C2",
        "Issue Tracker": "https://github.com/sumanthprabhu/C2/issues",
    },
    keywords="nlp, data curation, machine learning",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"],
    install_requires=base_packages,
    extras_require={"test": test_packages},
    python_requires=">=3.9",
)
