import setuptools

setuptools.setup(
    name='meteoFrance_data',
    version='1.1.1',
    author='Taoufik Bannour',
    author_email='taoufik.bannour.ext@suez.com',
    description='Un paquet des requêtes des données ouvertes de meteo-france',
    keywords='meteo,france, pypi, package',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    extras_require={
        'dev': ['check-manifest' ],
        # 'test': ['coverage'],
    },
    install_requires=[
    'geopy',
    'pandas'
    ]
)