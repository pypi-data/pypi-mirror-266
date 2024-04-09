from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 11',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='pseudofinch',
    version='0.0.2',
    description='Emulator of Finch 2.0 functions and constructors',
    long_description=open('README.txt').read(),
    url='',
    author='Quarksay',
    author_email='',
    license='MIT',
    classifiers=classifiers,
    keywords='robot',
    packages=find_packages(),
)