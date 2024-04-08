from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='qstd_async_tools',
    version='0.1.0',
    author='QuisEgoSum',
    author_email='subbotin.evdokim@gmail.com',
    description='Async tools',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/QuisEgoSum/qstd-async-tools',
    packages=find_packages(exclude=['tmp', 'example', '*test*']),
    install_requires=[],
    keywords='asyncio',
    python_requires='>=3.7',
    license='MIT'
)
