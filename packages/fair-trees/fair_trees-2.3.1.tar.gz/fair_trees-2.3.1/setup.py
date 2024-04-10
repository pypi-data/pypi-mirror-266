from setuptools import setup, find_packages

setup(
    name="fair_trees",
    version="2.3.1",
    packages=find_packages(),
    description="This package learns fair decision tree classifiers which can then be bagged into fair random forests, following the scikit-learn API standards.",
    author="Antonio Pereira Barata",
    author_email="apbarata@gmail.com",
    url="https://github.com/pereirabarataap/fair_tree_classifier",
    install_requires=[
        "scipy",
        "numpy",
        "pandas",
        "joblib",
        "scikit-learn"
    ],
)