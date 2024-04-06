from setuptools import setup, find_packages
with open('README.md', 'r') as file:
    long_description = file.read()
setup(
    name='swahilipro',
    version="2.3.0",
    long_description=long_description,
    long_description_content_type='text/markdown',

    description='A compiler package',
    author='Masota & Ngigi',
    author_email='bonniemasota@gmail.com',
    packages=['swahilipro'],
    entry_points={
        'console_scripts': ['swahilipro=swahilipro.shell:main']
    },
)
 #python setup.py sdist bdist_wheel
   # twine upload dist/* --verbose   
#pypi-AgEIcHlwaS5vcmcCJDFjYzhlNGJkLTlmMjUtNGRiOS1hNGNhLTcyMTA4NzI5ZjMzNgACKlszLCJmMDZmOTY2Mi1jMzFjLTQyNTMtYTBiYi1mZDRlOTUwMmMzMGYiXQAABiAAjYK6D8Dj8VNsSyZDuOYLZHk4zY8OLqdEVRg6q0Q11Q