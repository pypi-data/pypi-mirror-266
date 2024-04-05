import setuptools

PACKAGE_NAME = "groups-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/groups-local
    version='0.0.11',
    author="Circles",
    author_email="info@circles.life",
    description="PyPI Package for Circles groups-local Python",
    long_description="PyPI Package for Circles groups-local Python",
    long_description_content_type='text/markdown',
    url="https://github.com/circles-zone/group-main-local-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'PyMySQL>=1.0.2',
        'pytest>=7.4.0',
        'mysql-connector>=2.2.9',
        'logzio-python-handler>= 4.1.0',
        'database-infrastructure-local>=0.0.23',
        'user-context-remote>=0.0.58'
    ],
)
