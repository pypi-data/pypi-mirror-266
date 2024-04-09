import setuptools

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()
setuptools.setup(
    name='ANX',
    version='0.7.3',
    url='https://github.com/grayrail000/AndroidQQ',
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    license='',
    author='1x',
    author_email='',
    description='',
    install_requires=[
        'AndTools',
        'protobuf==4.23.4',
        'cryptography',
        'bs4',
        'urllib3==1.26.16',
        'pydantic',
        'requests',
        'python-box',
        'PySocks',
        'python-box'

    ]

)
