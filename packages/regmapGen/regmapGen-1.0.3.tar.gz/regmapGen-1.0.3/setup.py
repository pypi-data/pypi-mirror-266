import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Install package
setuptools.setup(
    name="regmapGen",
    version='1.0.3',
    author="paulmsv",
    author_email="bobkovpg@gmail.com",
    description="Генератор Регистровой Карты",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paulmsv/regmapGen",
    project_urls={
        'Documentation': 'https://regmapGen.readthedocs.io'
    },
    packages=setuptools.find_packages(exclude='tests'),
    package_data={'regmapGen': ['templates/*.j2']},
    entry_points={
        'console_scripts': [
            'regmapGen = regmapGen.__main__:main',
        ],
    },
    install_requires=[
        'pyyaml>=5.1',
        'jinja2',
        'wavedrom',
        'sphinx',
        'sphinxcontrib-wavedrom',
        'sphinx_rtd_theme',
        'pandas',
        'python-docx',
        'ruamel.yaml',
        'm2r2',
        'numpy',
        'pandoc',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)