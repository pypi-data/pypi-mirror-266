from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='qstd_logger_json_formatter',
    version='0.1.0',
    author='QuisEgoSum',
    author_email='subbotin.evdokim@gmail.com',
    description='Logging json formatter',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/QuisEgoSum/qstd-logger-json-formatter',
    packages=find_packages(exclude=['tmp', 'example']),
    install_requires=[],
    keywords='logging json formatter',
    python_requires='>=3.7',
    license='MIT'
)
