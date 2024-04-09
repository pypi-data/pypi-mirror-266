import setuptools

setuptools.setup(
    name="dp-launching-app",
    version="0.0.1",
    author="",
    author_email="",
    description="",
    long_description="",
    long_description_content_type="text/plain",
    url="",
    entry_points={
        "console_scripts": [
            "launching-app = dp.launching.cli.commands.launching:main",
        ]
    },
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.8",
    install_requires=[
        "fastapi",
        "uvicorn",
        "wcmatch",
        "pydantic>=1.10.5",
        "pydantic_cli>=4.3.0",
        "Deprecated",
        "dict-deep>=4.1.2",
        "kubernetes>=28.1.0",
    ],
)
