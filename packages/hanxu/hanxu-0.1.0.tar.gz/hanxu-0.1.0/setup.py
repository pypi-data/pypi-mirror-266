from setuptools import setup, find_packages

setup(
    name='hanxu',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        ip=ip.core:main
    ''',
    author="Your Name",
    author_email="deep.work.max@gmail.com",
    description="A package to get and count IP addresses",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Xu-Hardy/findyourip",
)
