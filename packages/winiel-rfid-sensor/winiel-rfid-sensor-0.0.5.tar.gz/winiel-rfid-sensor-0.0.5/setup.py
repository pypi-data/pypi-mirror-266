from setuptools import setup, find_packages

setup(
    name='winiel-rfid-sensor',
    version='0.0.5',
    description='PYPI tutorial package creation written by winiel',
    author='winiel',
    author_email='winiel@naver.com ',
    url='https://github.com/winiel',
    install_requires=['pyserial', 'pyusb'],
    packages=find_packages(exclude=[]),
    keywords=['winiel', 'rfid', 'sensor'],
    python_requires='>=3.9',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)