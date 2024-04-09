from setuptools import setup, find_packages

setup(
    name="llmreader",
    version="0.2.5",
    description="Intercept OpenAI inputs",
    author="Ethan Hou",
    author_email="ethanfhou10@gmail.com",
    packages=find_packages(),
    install_requires=[
        'openai'
    ],
    classifiers=[
        # Trove classifiers
        # Full list at https://pypi.org/classifiers/
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
