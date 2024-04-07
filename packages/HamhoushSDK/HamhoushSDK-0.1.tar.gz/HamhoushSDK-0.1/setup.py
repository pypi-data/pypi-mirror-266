from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='HamhoushSDK',
    author='Smilinno',
    packages=['Hamhoush'],
    # Needed for dependencies
    install_requires=['numpy','requests'],
    # *strongly* suggested for sharing
    version='0.1',
    description='hamhoush platform sdk',
)