from setuptools import setup, find_packages

setup(
    name='feature_engineering',
    version='2.1.3',
    packages=find_packages(),
    description='Unleash the Power of Your Data with Feature Engineering: The Ultimate Python Library for Machine Learning Preprocessing and Enhancement',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Kwadwo Daddy Nyame Owusu - Boakye',
    author_email='kwadwo.owusuboakye@outlook.com',
    url='https://github.com/knowusuboaky/feature_engineering',
    install_requires=[
        'pandas>=1.1.5',
        'numpy>=1.19.5',
        'scikit-learn>=0.24',
        'imbalanced-learn>=0.7.0',
        'holidays>=0.10.3',
        'ipywidgets>=7.5.1'
    ],
    python_requires='>=3.6',
    keywords='machine learning, data preprocessing, feature engineering, data transformation, data cleaning, outlier handling, imputation, scaling, one-hot encoding, feature selection, variance threshold, correlation filtering, embedded methods, wrapper methods, class imbalance, sampling techniques, hyperparameter tuning, model optimization, categorical data processing, numeric data processing, date feature extraction, custom transformers, Python, data science, predictive modeling, classification, regression, ML workflows, data analysis, data enrichment, model performance improvement',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    
)
