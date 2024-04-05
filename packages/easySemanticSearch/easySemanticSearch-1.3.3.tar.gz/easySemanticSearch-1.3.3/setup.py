from setuptools import setup, find_packages

setup(
    name='easySemanticSearch',
    version='1.3.3',
    author='Abhishek Venkatachalam',
    author_email='abhishek.venkatachalam06@gmail.com',
    description='UserFriendly implementation of Highly optimized advanced semantic search.',
    long_description=(
        "For more information about the author, visit [LinkedIn](https://www.linkedin.com/in/abhishek-venkatachalam-62121049/).\n\n"
        + open('README.md').read()
    ),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'sentence-transformers',
        'numpy',
        'pandas'
    ],
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)