from setuptools import setup, find_packages


def read_readme() -> str:
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='weasyform',
    version='0.0.8',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'WeasyPrint>=61.0'
    ],

    url='https://github.com/Salamek/weasyform',
    license='BSD',
    author='Adam Schubert',
    author_email='adam.schubert@sg1-game.net',
    description='Simple form support for WeasyPrint',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
    ],
    python_requires='>=3.4',
    project_urls={
        'Release notes': 'https://github.com/Salamek/weasyform/releases',
    },
)
