import setuptools

PACKAGE_NAME = "action-items-local"
package_dir = PACKAGE_NAME.replace("-", "_")


setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.7',  # update only the minor version each time # https://pypi.org/project/action-items-local/
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles action-items-local Python",
    long_description="PyPI Package for Circles action-items-local Python",
    long_description_content_type='text/markdown',
    url="https://github.com/circles-zone/action-item-local-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pytest>=7.4.0',
        'logzio-python-handler>= 4.1.0',
        'user-context-remote>=0.0.58',
        'python-sdk-remote>=0.0.27',
        'database-mysql-local>=0.0.221',
        'logger-local>=0.0.108',
        'language-remote>=0.0.15'
    ],
)
