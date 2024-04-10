import setuptools
import htmltagparse

with open("README.md", "r") as f:
    readme = f.read()

with open("requirements.txt", 'r') as f:
    requirements = f.read().split('\n')

setuptools.setup(
    name="htmltagparse",
    version=htmltagparse.__version__,
    author=htmltagparse.__author__,
    maintainer=htmltagparse.__author__,
    description=htmltagparse.__description__,
    url="https://github.com/xyzpw/htmltagparse/",
    long_description=readme,
    long_description_content_type="text/markdown",
    license=htmltagparse.__license__,
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
    ],
    install_requires=requirements,
)
