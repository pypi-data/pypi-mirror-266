import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pythagoras"
    ,version="0.10.43"
    ,author="Volodymyr (Vlad) Pavlov"
    ,author_email="vlpavlov@ieee.org"
    ,description= "Simple framework for planet-scale "
                  + "idempotent computations in Python."
    ,long_description=long_description
    ,long_description_content_type="text/markdown"
    ,url="https://github.com/vladlpavlov/pythagoras"
    ,packages=["pythagoras"
        , "pythagoras._01_foundational_objects"
        , "pythagoras._02_ordinary_functions"
        , "pythagoras._03_autonomous_functions"
        , "pythagoras._04_idempotent_functions"
        , "pythagoras._05_events_and_exceptions"
        , "pythagoras._06_swarming"
        , "pythagoras._07_mission_control"
        , "pythagoras._99_misc_utils"
        ]
    ,classifiers=[
        "Development Status :: 3 - Alpha"
        , "Intended Audience :: Developers"
        , "Intended Audience :: Science/Research"
        , "Programming Language :: Python"
        , "Programming Language :: Python :: 3"
        , "License :: OSI Approved :: MIT License"
        , "Operating System :: OS Independent"
        , "Topic :: Scientific/Engineering"
        , "Topic :: Scientific/Engineering :: Information Analysis"
        , "Topic :: Software Development :: Libraries"
        , "Topic :: Software Development :: Libraries :: Python Modules"
    ]
    ,keywords='cloud, ML, AI, serverless, distributed, parallel'
              ', machine-learning, deep-learning, pythagoras'
    ,python_requires='>=3.10'
    ,install_requires=[
        "persidict"
        , "lz4"
        , 'joblib'
        , 'numpy'
        , 'scipy'
        , 'pandas'
        , 'scikit-learn'
        , 'jsonpickle'
        , 'psutil'
        , 'boto3'
        , 'moto'
        , 'pytest'
        , 'autopep8'
        , 'torch'
        , 'keras'
        , 'tensorflow'
    ]

)