import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cicpacgen",
    version="0.0.2",
    author="Carsten Wulff",
    author_email="carsten@wulff.no",
    description="Custom IC Creator Package outline generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wulffern/cicpacgen",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    entry_points = {'console_scripts': [
        'cicpacgen = cicpacgen.cicpacgen:pacgen',
    ]},
    install_requires = 'PyYAML click svgwrite numpy pandas svglib reportlab  '.split(),
    classifiers = [
        'Development Status :: 1 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering',
    ],
)
