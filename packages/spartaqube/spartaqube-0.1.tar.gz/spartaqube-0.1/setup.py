import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spartaqube", # Replace with your own username
    version="0.1",
    author="Spartacus",
    author_email="spartacloud@gmail.com",
    description="spartaqube application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://spartaqube.com",
    packages=setuptools.find_packages(),
    install_requires=[
        'channels==3.0.4',
        'cloudpickle',
        'cx_Oracle',
        'django>=4.0,<5.0',
        'django-async',
        'django-async-orm',
        'django-channels',
        'django-cors-headers',
        'django_debug_toolbar',
        'django-picklefield',
        'django-prometheus',
        'djangorestframework',
        'duckdb',
        'ipython==8.17.2',
        'ipykernel==6.29.4',
        'jupyter_client',
        'jupyter_core',
        'jupyterlab',
        'mysql-connector-python',
        'numpy',
        'pandas',
        'psycopg2',
        'pymongo',
        'pymssql',
        'PyMySQL',
        'pyodbc',
        'python-dateutil',
        'pytz',
        'redis',
        'requests',
        'requests-oauthlib',
        'tinykernel',
        'tqdm',
        # Add any other dependencies your project requires
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)