import setuptools

setuptools.setup(
    name="qtlink",
    version="1.0.6",
    author="NanHaiLoong",
    author_email="nanhai@163.com",
    description="a ui framework based on pyside6",
    long_description='a ui framework based on pyside6',
    long_description_content_type="text/markdown",
    url="https://gitee.com/darlingxyz/qtlink",
    install_requires=['PySide6', 'matplotlib', 'numpy'],
    packages=setuptools.find_packages(include=['qtlink', 'qtlink.*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
