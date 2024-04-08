from setuptools import setup
import os

HERE = os.path.dirname(__file__)
VERSION_FILE = os.path.join(HERE, "VERSION.txt")

setup(
    name="pyvncs",
    version_config={
        "count_commits_from_version_file": True,
        "template": "{tag}",
        "dev_template": "{tag}.dev.{ccount}",
        "dirty_template": "{tag}.dev.{ccount}",
        "version_file": VERSION_FILE,
    },
    setup_requires=["setuptools-git-versioning"],
    description="A 3rd-party package of pyvncs since the author has not published it to pypi",
    long_description="A 3rd-party package of pyvncs since the author has not published it to pypi",
    url="http://github.com/darkpixel/pyvncs",
    author="Matias Fernandez",
    author_email="matias.fernandez@gmail.com",
    packages=["pyvncs"],
    install_requires=["pyDes", "pynput", "numpy", "Pillow-PIL"],
    zip_safe=False,
)
