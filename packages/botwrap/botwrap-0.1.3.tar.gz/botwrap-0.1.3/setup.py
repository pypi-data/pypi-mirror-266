from setuptools import setup, find_packages

setup(
    name='botwrap',
    version='0.1.3',
    author='BizPrincess',
    author_email='professionallyjami@gmail.com',
    description='A convenient wrapper for the OpenAI API.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/BizPrincess/botwrap',
    packages=find_packages(),
    install_requires=[
        'aiohttp==3.9.3',
        'attrs==23.2.0',
        'beautifulsoup4==4.12.3',
        'certifi==2023.11.17',
        'charset-normalizer==3.3.2',
        'click==8.1.7',
        'Flask==3.0.1',
        'httpx==0.26.0',
        'Jinja2==3.1.3',
        'openai==1.10.0',
        'psycopg2-binary==2.9.9',
        'requests==2.31.0',
        'urllib3==2.1.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

