from setuptools import setup, find_packages

setup(
    name="ipython_openai",
    version="0.0.1",
    author="Jordan Sitkin",
    author_email="jordan@fiftyfootfoghorn.com",
    description="An IPython extension for interacting with OpenAI's models",
    long_description=open('readme.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dustmason/ipython_openai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: IPython",
    ],
    python_requires='>=3.6',
    install_requires=[
        "ipython>=7.0",
    ],
    entry_points={
        'ipython.extensions': [
            'ipython_openai = ipython_openai:load_ipython_extension',
        ],
    }
)
