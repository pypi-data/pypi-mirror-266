from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
]

setup(
    name='pamqualeLabsTasks',
    version='0.0.1',
    description='Python package for lab tasks',
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type='text/markdown',
    url='',
    author='Pamquale Tagaromus',
    author_email='pamquale@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='lab tasks',
    packages=find_packages(),
    install_requires=[],
)
