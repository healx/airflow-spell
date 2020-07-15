from setuptools import setup, find_packages

setup(
    name="airflow-spell",
    version="0.0.3",
    author="Dan O'Donovan",
    author_email="dan.odonovan@healx.io",
    description="Apache Airflow integration for spell.run",
    packages=find_packages(include=["airflow_spell", "airflow_spell.*"]),
    install_requires=[
        "apache-airflow>=1.10.2,<2.0",
        "spell>=0.38.4,<1.0",
    ]
)
