from setuptools import setup, find_packages

setup(
    name='binance_network',
    version='0.1.2',
    packages=find_packages(),
    description='This is a Python wrapper for the Binance network',
    url='https://github.com/zz-big/binance_network.git',
    download_url = 'https://github.com/zz-big/binance_network.git',
    author='zz-big',
    license='MIT',
    author_email='',
    install_requires=['binance-connector'],
    keywords='binance exchange network example',
    classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)