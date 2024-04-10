from setuptools import setup

setup(
    name="pracscode4",
    version="0.1",
    description="Python package to automatically download a file upon installation",
    author="Your Name",
    packages=["pracscode4"],
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "pracscode4_installer = pracscode4.installer:main"
        ]
    }
)
