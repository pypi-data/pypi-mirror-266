from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Simplify machine learning tasks with easy-to-use tools and utilities.'
LONG_DESCRIPTION = """
MLEase is a comprehensive Python package that simplifies machine learning tasks by providing many easy-to-use tools and utilities. It aims to streamline the entire machine learning workflow, from data preprocessing to model evaluation, making it accessible to both beginners and experienced practitioners.

Key features include:

- Missing value imputation: Handle missing data in your dataset using various strategies such as mean, median, mode imputation, or advanced techniques like KNN imputation.
- Outlier detection and removal: Identify and remove outliers from your dataset using methods like standard deviation, IQR, Mahalanobis distance, or anomaly detection algorithms such as Isolation Forest, One-Class SVM, Elliptic Envelope, and Local Outlier Factor.
- Feature scaling: Scale your features to a standard range using methods like Min-Max scaling or standardization.
- and more.

MLEase aims to simplify the machine learning process and empower users to build more robust and accurate models with ease.
"""


# Setting up
setup(
    name="MLEase",
    version=VERSION,
    author="Harikrishna Dev",
    author_email="harikrish0607@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/harikrishnad1997/MLEase',
    packages=find_packages(),
    install_requires=[],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'numpy'

    keywords=['python', 'machine learning', 'data science'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ]
)
