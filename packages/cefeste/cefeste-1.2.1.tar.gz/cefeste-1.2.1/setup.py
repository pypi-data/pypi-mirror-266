from setuptools import setup, find_packages

setup(
    name="ce-feste",
    version="1.2.0",
    description="Package for Feature Selection, Transformation, Elimination",
    author="DAT Team",
    url="https://dev.azure.com/credem-data/DAT/_git/ce-feste",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_packages(where="src", exclude=["test"]),
    package_dir={"": "src"},
    # Usato solo con 3.9 e 3.10
    python_requires=">=3.9, <4",
    install_requires=[
        "typed-ast==1.5.4",
        "numpy==1.22.4",
        "pandas==1.4.2",
        "scikit-learn>=1.1.1",
        "scipy>=1.8.1",
        "statsmodels>=0.13.2",
        "PyYAML>=6.0",
        "shap==0.41.0",
        "ipython",
    ],
)
