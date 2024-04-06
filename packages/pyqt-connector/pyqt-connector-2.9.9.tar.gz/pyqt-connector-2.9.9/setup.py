from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyqt-connector",
    version="2.9.9",
    author="Weto-bi",
    description="A seamless integration bridge between PyQt and PostgreSQL, enabling rapid development of database-backed PyQt applications with robust data handling capabilities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "psycopg2>=2.9.9",
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
