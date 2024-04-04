from setuptools import setup, find_packages

setup(
    name='list_flatten_z',
    version='0.5',
    packages=find_packages(),
    install_requires=['pandas'],
    author='Neu_Basis',
    author_email='streamingandflow@outlook.com',
    description='A package to flatten lists using Pandas',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/list-flatten',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)