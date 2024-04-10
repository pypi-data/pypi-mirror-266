import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name='navam',
    version='1.0.0',
    author='Nava Teja',
    author_email='mushamnavam9530@gmail.com',
    description="Encrypt and decrypt any file using Navam's Encryption Technique",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license = "MIT",
    url='https://github.com/Navam9530/Navams_Encryption_Technique',
    keywords = "Encryption Bit-Manipulation Cryptography",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
    ],
)