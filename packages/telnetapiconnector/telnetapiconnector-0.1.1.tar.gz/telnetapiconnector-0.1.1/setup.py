import setuptools

requirements = []

with open("requirements.txt") as req:
    for line in req.readlines():
        line = line.strip()
        if line:
            requirements.append(line)

setuptools.setup(
    name='telnetapiconnector',
    version='0.1.1',
    author='Nikita Kudryashov',
    author_email='nikitemailua@gmail.com',
    description='A Python library for interacting with the Telnet',
    packages=['telnetapiconnector'],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires='>=3.10'
)
