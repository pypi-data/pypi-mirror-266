from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="lebon",
    version="0.1.5",
    author="Lebon James",
    description="You are my sunshine, my only sunshine.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["pyperclip", "google-generativeai", "pyautogui"],
    entry_points={
        "console_scripts": [
            "lebon=lebon.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={'lebon': ['assets/*.json']},
    include_package_data=True,
    license="MIT"
)