from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='noohayo',
    version='1.0.4',
    description="command line interface tool that displays a banner when ever you open a new ternimal tab.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'argparse', 'appdirs', 'psutil'
    ],
    entry_points={
        'console_scripts': [
            'noohayo=noohayo.noohayo:main',
        ],
    },
)
