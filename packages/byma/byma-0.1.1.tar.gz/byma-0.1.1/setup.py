from setuptools import setup, find_packages

DESCRIPTION = 'Numerical Mathematics Package'
LONG_DESCRIPTION = 'A Numerical Mathematics Packages with an easier and clean user interface.'

# Setting up
setup(
    name="byma",
    include_package_data=True,
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    author="@b64-Lorenzo (Lorenzo Zambelli)",
    author_email="<bytemath@lorenzozambelli.it>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION + '\n\n' + open('CHANGELOG.txt').read(),
    packages=find_packages(),
    install_requires=[
        'numpy>=1.1', 
        'scipy>=1.1', 
        'matplotlib>=3.6'
        ],
    keywords=['python', 'scientific', 'numerical', 'bifurcation'],
    classifiers=[ "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)