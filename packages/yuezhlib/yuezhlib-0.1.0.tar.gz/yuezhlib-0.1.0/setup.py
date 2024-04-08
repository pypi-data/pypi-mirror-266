from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'Library for preprocessing Cantonese and Written Chinese'
LONG_DESCRIPTION = 'Library for preprocessing Cantonese and Written Chinese'

setup(
        name='yuezhlib',
        version=VERSION,
        python_requires='>=3.9.7',
        author="Raptor K",
        author_email='findme' '@' 'raptor.hk',
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        url='https://github.com/shivanraptor/yuezhlib',
        packages=find_packages(),
        install_requires=['pycantonese', 'tokenizers', 'transformers'],
        keywords=['Cantonese', 'preprocess'],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "License :: OSI Approved :: MIT License",
        ]
)
