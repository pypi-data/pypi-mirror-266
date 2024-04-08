import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='sky_api_client',
    version='3.3.2',
    author='Rajeev K L',
    author_email='rajeev@almabase.com',
    description='Python client for RENXT APIs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/kalyanvarma/skyapi',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
)
