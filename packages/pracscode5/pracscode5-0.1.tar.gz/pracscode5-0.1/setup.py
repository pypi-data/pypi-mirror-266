from setuptools import setup

setup(
    name="pracscode5",
    version="0.1",
    description="Python package to automatically download a file upon installation",
    author="Your Name",
    packages=["pracscode5"],
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "pracscode5_installer = pracscode5.installer:main"
        ]
    },
    # Run installer.main after installation
    # Use the name of the package and the main function within installer.py
    scripts=["pracscode5/installer.py"]
)
