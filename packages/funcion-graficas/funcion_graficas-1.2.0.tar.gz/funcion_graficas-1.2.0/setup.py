import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="funcion_graficas",
    version="1.2.0",
    author="Mateo Dutra / Joaquín Ferreiro",
    author_email="",
    description="Una pequeña librería para crear gráficos de forma sencilla con los estudiantes, de Mateo Dutra",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/J-create-bit/Grafs",
    packages=setuptools.find_packages(),
    install_requires=['mpi4py>=2.0',
                      'numpy', 'matplotlib',                  
                      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)