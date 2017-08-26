from setuptools import find_packages, setup

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="sniper",
    version="0.0.6",
    description="an asynchronous restful web framework base on asyncio",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/lexdene/py-sniper",
    license='GPLv3',
    author="Elephant Liu",
    author_email="lexdene@gmail.com",
    packages=find_packages(exclude=['tests/*']),
    platforms=['any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
