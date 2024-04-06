from setuptools import setup
import hyphenfrac

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="hyphenfrac",
    author=hyphenfrac.__author__,
    maintainer=hyphenfrac.__author__,
    version=hyphenfrac.__version__,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Environment :: Console :: Curses",
        "Environment :: Console",
    ],
    url="https://github.com/xyzpw/hyphenfrac/",
    description=hyphenfrac.__description__,
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    license="MIT",
)
