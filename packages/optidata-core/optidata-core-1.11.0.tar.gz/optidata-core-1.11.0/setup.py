from setuptools import setup, find_packages

VERSION = '1.11.0'  # settings.APP_VERSION
DESCRIPTION = 'Paquete de Python para OptiData'
LONG_DESCRIPTION = 'Paquete para OptiData que contiene funcionalidades para realizar una Conciliación con Pandas y Vaex'

# Configurando
setup(
    name="optidata-core",
    version=VERSION,
    author="Gonzalo Torres Moya",
    author_email="<gtorres@optimisa.cl>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(where="app"),
    package_dir={"": "app"},
    keywords=['python', 'optidata-core'],
    license="MIT",
    install_requires=[
        "Flask-Bcrypt==1.0.1",
        "Flask>=3.0.2",
        "numpy>=1.26.4",
        "openpyxl>=3.1.2",
        "pandas>=2.2.1",
        "pymongo==4.3.3",
        "pysftp==0.2.9",
        "vaex>=4.17.0",
        "kafka-python>=2.0.2",
        "joblib>=1.3.2",
        "paramiko~=3.4.0",
        "oracledb==2.1.0",
        "sqlalchemy==2.0.28",
        "APScheduler>=3.10.4",
        "flask-restx>=1.3.0",
        "Fernet==1.0.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9"
)
