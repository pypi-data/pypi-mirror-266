from setuptools import setup, find_packages

setup(
    name='football-stats-scraper',
    version='0.1.0',
    author='John Murtagh',
    author_email='john90murtagh@gmail.com',
    description='A Python script to scrape football league tables and fixtures',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/football-stats-scraper',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'football-stats-scraper=main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
