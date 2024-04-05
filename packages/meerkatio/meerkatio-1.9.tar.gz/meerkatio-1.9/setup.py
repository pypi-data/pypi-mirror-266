from setuptools import setup, find_packages

setup(
    name='meerkatio',
    version='1.9',
    packages=find_packages(),
    package_data={'meerkat': ['ping_sounds/*.mp3']},
    include_package_data=True,
    install_requires=[
        "requests",
        "click",
        "ipython"
    ],
    entry_points='''
        [console_scripts]
        meerkat=meerkat.cli:meerkat
    ''',
    author="MeerkatIO",
    description="Simple notification tool for multi-tasking developers",
    long_description=open("documentation.md").read(),
    long_description_content_type="text/markdown",
    license=open("LICENSE").read()
    # Add other metadata such as author, author_email, description, etc.
)
