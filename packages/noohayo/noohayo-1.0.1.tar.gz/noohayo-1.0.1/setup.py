from setuptools import setup, find_packages

setup(
    name='noohayo',
    version='1.0.1',
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
