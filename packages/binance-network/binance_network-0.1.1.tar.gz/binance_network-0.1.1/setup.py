from setuptools import setup, find_packages

setup(
    name='binance_network',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        "binance-connector"
    ],
    entry_points={
        'console_scripts': [
            'binance_network=binance_network.binance_coin_network:main',
        ],
    },
)