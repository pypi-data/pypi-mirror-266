from setuptools import setup, find_packages

requirements = [
    "pyside6>=6.4.1",
    "torch>=2.0.0",
    "torchvision>=0.14.1",
    "wget>=3.2",
    "scikit-image>=0.19.3",
    "numpy>=1.23.5",
    "tqdm>=4.64.1",
    "yacs>=0.1.8",
]

setup(
    name="ciliaseg",
    version="0.0.5.dev20240404",
    packages=find_packages(),
    entry_points={"console_scripts": ["ciliaseg = ciliaseg.__main__:launch"]},
    install_requires=requirements,
)
