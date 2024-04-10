from setuptools import setup, find_packages

setup(
    name="sdevelo",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'anndata>=0.10.7',
        'matplotlib>=3.7.1', 
        'numpy>=1.23.5', 
        'scipy>=1.8.1', 
        'scvelo>=0.2.5', 
        'seaborn>=0.11.2', 
        'torch>=1.13.1'
    ],
    author="Xu Liao",
    author_email="xu.smooth.liao@gmail.com",
    description="SDEvelo: a deep generative approach for transcriptional dynamics with cell-specific latent time and multivariate stochastic modeling",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Liao-Xu/SDEvelo",
    license="LICENSE",
    classifiers=[
        # Classifiers help users find your project by categorizing it.
        # For a list of valid classifiers, see https://pypi.org/classifiers/
        "Development Status :: 1 - Planning", 
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
