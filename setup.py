from distutils.core import setup

setup(
    name='gyik_scraper',
    version='0.1-DEV',
    packages=['db_tools','scraper'],
    url='https://github.com/dsuveges/gyik_scaper',
    license='MIT',
    author='Daniel Suveges',
    author_email='suvi.dani@gmail.com',
    description='These packages provides tools to scrape data from gyakorikerdesek.hu and load into an SQLite database.'
)
