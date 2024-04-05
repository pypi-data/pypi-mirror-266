from setuptools import setup, find_packages

def read_requirements():
    with open("requirements.txt", "r") as req:
        content = req.read()
        requirements = content.split("\n")
    return requirements


setup(
    name="dalpha_ai_cpu",
    version="0.3.0",
    packages=find_packages(),
    install_requires=read_requirements(),
)
