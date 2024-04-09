import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="OncoBLADE",
    version="1.0.0",
    author="Yongsoo Kim",
    author_email="yo.kim@amsterdamumc.nl",
    description="OncoBLADE - extended version of BLADE tailored for cancer application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tgac-vumc/oncoBLADE",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numba', 'numpy', 'scipy', 'scikit-learn', 'joblib'
        ],
    python_requires='>=3.6',
)
