from setuptools import setup, find_packages

requirements = [
    "requests",
    "websocket-client==1.3.1", 
    "setuptools", 
    "json_minify", 
    "six",
    "aiohttp",
    "websockets"
]

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name="ZAmino.fix",
    author="ZOOM",
    version="1.1.2",
    description="Aminofix update. https://t.me/ZAminoZ",
    packages=find_packages(),
    long_description=long_description,
    install_requires=requirements,
    keywords=[
    	'ZAmino'
    	'ZAmino.fix'
        'aminoapps',
        'amino.fix',
        'amino',
        'amino-bot',
    ],
    python_requires='>=3.6',
)
