from setuptools import setup, find_packages

setup(
    name="something-else",
    version="0.0.5",
    author="Dan O'Donovan",
    author_email="dan.odonovan@healx.io",
    description="Apache Airflow integration for spell.run",
    packages=find_packages(include=["airflow_spell", "airflow_spell.*"]),
    install_requires=["apache-airflow>=1.10.2,<3.0", "spell>=0.38.4,<1.0",],
)
