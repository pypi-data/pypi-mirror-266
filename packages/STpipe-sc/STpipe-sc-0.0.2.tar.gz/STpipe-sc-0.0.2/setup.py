from setuptools import setup, find_namespace_packages

setup(
    name='STpipe-sc',
    version='0.0.2',
    description=('STpipe is designed to analyze spatial transcriptomic data.'),
    author='Mao Guangyao',
    license='MIT License',
    url='https://github.com/mgy520/STpipe',
    packages=find_namespace_packages(),
    python_requires='==3.8.18',
    install_requires=[
            'rpy2==3.5.15',
            'anndata2ri==1.3.1',
            'numpy==1.24.4',
            'diffxpy==0.7.4',
            'scipy==1.10.1',
            'pandas==2.0.3',
            'anndata==0.9.2',
            'shapely==2.0.3',
            'dask==2023.5.0',
            'numba==0.58.1',
            'pca==2.0.5',
            'openTSNE==1.0.1',
            'igraph==0.11.4',
            'sinfonia==0.0.3',
            'tangram-sc==1.0.4',
            'scanorama==1.7.4',
            'matplotlib==3.7.4',
            'seaborn==0.13.2',
            'adjustText==1.1.1',
            'scikit-learn==1.3.2',
            'scikit-misc==0.2.0',
            'scikit-image==0.21.0'
    ]
)