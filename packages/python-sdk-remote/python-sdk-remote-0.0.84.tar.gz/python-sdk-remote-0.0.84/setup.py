import setuptools

PACKAGE_NAME = "python-sdk-remote"
package_dir = PACKAGE_NAME.replace("-", "_")

# used by python -m build
# python -m build needs pyproject.toml or setup.py
setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.84',  # https://pypi.org/project/python-sdk-remote/
    author="Circles",
    author_email="info@circles.life",
    description="PyPI Package for Circles Python SDK Local Python",
    long_description="This is a package for sharing common functions used in different repositories",
    long_description_content_type="text/markdown",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "python-dotenv",
        "url-remote"
    ]
)
