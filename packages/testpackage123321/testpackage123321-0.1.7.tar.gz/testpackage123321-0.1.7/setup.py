from setuptools import setup, find_packages
from pkg_resources import EntryPoint

setup(
    name='testpackage123321',
    version='0.1.7', # all versions prior to launch will go into 0.0.1.--
    packages=find_packages(),
    license='MIT',
    description='This library is to search the best parameters across different steps of the RAG process.',
    entry_points={
        'console_scripts': [
            'check_version = testpackage.check_version:check_python_version',  # Replace with your script path
        ]
    },
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ankit',
    author_email='a.baliyan008@gmail.com',
    url='https://github.com/hidevscommunity/gen-ai-library/tree/main/Ankit',
    install_requires=[
        'langchain==0.1.13',
        'langchain-openai>=0.1.1',
        'trulens-eval==0.27.0',
        'chromadb==0.4.24',
        'sentence-transformers==2.6.1',
        'unstructured[pdf]==0.13.0',
    ],
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ]

)
