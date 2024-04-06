from setuptools import find_packages, setup

setup(
    name='landborn',
    packages=find_packages(include=['landborn']),
    version='0.2.4',
    description='Landborn Visualization Library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Molly Nelson',
    author_email="mollyynelson@gmail.com",
    license='MIT',
    install_requires=['pandas', 'numpy', 'matplotlib'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==8.0.0'],
    test_suite='tests'
)