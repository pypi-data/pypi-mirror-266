from setuptools import setup, find_packages

requirements = [
    'aiohttp',
    'pycryptodome',
    'pydantic==1.10.12',
    'aiofiles',
]

with open('README.md', encoding='UTF-8') as f:
    readme = f.read()

setup(
    name='aiorubika',
    version='0.0.2',
    author='amirali irvany',
    author_email='dev.amirali.irvany@gmail.com',
    description=' Rubika API Framework for Python',
    keywords=['rubika', 'aiorubika', 'chat', 'bot', 'robot', 'asyncio'],
    long_description=readme,
    python_requires="~=3.7",
    long_description_content_type='text/markdown',
    url='https://github.com/metect/rubika',
    packages=find_packages(),
    exclude_package_data={'': ['*.pyc', '*__pycache__*']},
    install_requires=requirements,
    extras_require={
        'cv': ['opencv-python'],
        'pil': ['pillow']
    },
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Internet',
        'Topic :: Communications',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ],
)
