from setuptools import setup, find_packages

setup(
    name="basic-ml-project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0",
        "mlflow>=2.13.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "joblib>=1.3.0"
    ],
    python_requires=">=3.10",
) 