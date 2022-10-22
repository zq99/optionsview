from setuptools import setup

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
]

setup(
    name='optionsview',
    version='0.0.1',
    packages=['options', 'testing'],
    url='https://github.com/zq99/optionsview',
    python_requires=">=3.7",
    classifiers=classifiers,
    license='GPL-3.0+',
    author='zq99',
    author_email='zq99@hotmail.com',
    keywords=['OPTIONS', 'STRADDLE', 'DATA', 'TRADING', 'CALLS', 'PUTS', 'ALGOTRADING',
              'YFINANCE', 'YAHOO FINANCE', 'EXPIRATION DATES', 'SPREADS', 'STOCK MARKET', 'TICKER'],
    install_requires=[
        'yfinance',
        'pandas',
        'numpy'
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown; charset=UTF-8; variant=GFM',
    description='Download options call/put data for any ticker in a trader friendly format',
)
