from setuptools import setup, find_packages

setup(
    name='clstr',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'colorama',
        'mkl-service',
        'numpy',
        'scipy',
        'setuptools',
        'tqdm',
        'wheel',
    ],
)
