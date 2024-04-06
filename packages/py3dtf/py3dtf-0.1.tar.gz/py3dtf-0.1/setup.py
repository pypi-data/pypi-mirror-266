import numpy
from setuptools import setup
from Cython.Build import cythonize


setup(
    name="py3dtf",
    description="Simple 3D Transforms in Python",
    author="Daniel Dugas",
    version="0.1",
    packages=["py3dtf"],  # if adding more folders, schema.tools, etc...
    # ext_modules=cythonize("cyschema/fast_ops.pyx", annotate=True),
    python_requires=">=3.6",
    install_requires=[
        "matplotlib",
        "numpy",
    ],
    include_dirs=[numpy.get_include()],
    # To package data files, they
    # 1) should be inside the schema folder (so that they end up in site-packages/schema/... dir structure)
    # 2) be included in MANIFEST.in
    # 3) the flag include_package_data=True needs to be in setup.py
    # the package_data flag doesn't do anything AFAICT
    package_data={"py3dtf": ["data/*"]},
    include_package_data=True,
)
