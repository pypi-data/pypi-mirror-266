from setuptools import setup, find_packages


with open("README.md") as f:
    LONG_DESCRIPTION = "\n" + f.read()

VERSION = '0.1.2'
DESCRIPTION = 'AI based optimized parameter estimation for ML models.'
# LONG_DESCRIPTION = 'AI based optimized parameter estimation of ML models using Hybrid of Genetic Algorithm and Simulated Annealing. based on the paper by Jegadit S Saravanan @ https://ieeexplore.ieee.org/document/10308077'


setup(
    name='jss_optimizer',
    version=VERSION,
    install_requires=['numpy', 'tqdm'],
    author='Jegadit S Saravanan',
    author_email='jegaditssaravanan@yahoo.com',
    # description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['machine-learning', 'parameter optimization', 'genetic algorithm', 'simulated annealing'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
