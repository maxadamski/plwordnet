import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name='plwordnet',
    version='0.1.4',
    description='Library for using the Polish Wordnet in the plwnxml format',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/maxadamski/plwordnet',
    author='Max Adamski',
    author_email='max@maxadamski.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Natural Language :: Polish',
    ],
    packages=['plwordnet'],
    include_package_data=True,
    python_requires='>=3.7',
    setup_requires=['pip', 'setuptools', 'wheel'],
    install_requires=['lxml'],
)

