from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='coinprice',
    version='1.3.0',
    author='Bohdan (7GitGuru)',
    author_email='Bohd4n@proton.me',
    description='CryptoTracker is a command-line tool for tracking cryptocurrency prices across multiple exchanges.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        "requests",
        "colorama",
    ],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='cryptocurrency, crypto, bitcoin, ethereum, tracking, prices, finance, binance, okx, bybit, coinbase',
    project_urls={
        'GitHub': 'https://github.com/7GitGuru/crypto-tracker/tree/cmd',
        'Documentation': 'https://github.com/7GitGuru/crypto-tracker/blob/cmd/README.md',
        'Website': 'https://cryptotrack3r.vercel.app/'
    },
    entry_points={
        'console_scripts': [
            'price = crypto_tracker.main:main',
        ],
    },
    python_requires='>=3.8'

)
