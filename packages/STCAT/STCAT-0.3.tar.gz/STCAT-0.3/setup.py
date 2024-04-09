import setuptools

def get_requirements():
    with open("requirements.txt", "rt", encoding="utf-8") as fh:
        return [line.strip() for line in fh.readlines()]

setuptools.setup(
    name='STCAT',
    version='0.3',
    packages=setuptools.find_packages(),
    install_requires=get_requirements(),
    include_package_data=True,
    python_requires='>=3.8',
    url="https://github.com/GuoBioinfoLab/STCAT",
    description="An automated T cell type annotation tool for scRNA-seq datasets.",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        ],
    license="MIT"

)
