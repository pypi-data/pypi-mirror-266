'''Setup for DimmerAttenuation'''
from numpy.distutils.core import Extension
from numpy.distutils.core import setup

with open("README.md","r",encoding="utf-8") as fh:
    long_description = fh.read()

with open("version.txt","r",encoding="utf-8") as vh:
    version_description = vh.read()

ext1 = Extension(  name='dimmerattenuation.flib',
                   sources=[ 'src/fortran/Reddening/DataTypes.f90',
                             'src/fortran/Reddening/SPLINE1DArr.f90',
                             'src/fortran/Reddening/CAF__LawOPT.f90',
                             'src/fortran/Reddening/CL_R_LawOPT.f90',
                             'src/fortran/Reddening/J13__LawOPT.f90',
                             'src/fortran/Reddening/S79__LawOPT.f90',
                             'src/fortran/Reddening/CALR_LawOPT.f90',
                             'src/fortran/Reddening/Leitherer02.f90',
                             'src/fortran/Reddening/CCMR_LawOPT.f90',
                             'src/fortran/Reddening/H83gaLawOPT.f90',
                             'src/fortran/Reddening/O_Donnell94.f90', ]
                )

setup( name='dimmerattenuation',
       version=version_description,
       ext_modules=[ ext1 ],
       extra_compile_args=['-O3'],
       description='DimmerAttenuation is a standalone python library with \
Fortran legacy routines for absorption (attenuation).',
       long_description=long_description,      # Long description read from the the readme file
       long_description_content_type="text/markdown",
       author='Jean Gomes',
       author_email='antineutrinomuon@gmail.com',
       url='https://github.com/neutrinomuon/DustyGlow',
       install_requires=[ 'numpy','matplotlib' ],
       classifiers=[
           "Programming Language :: Python :: 3",
           "Programming Language :: Fortran",
           "Operating System :: OS Independent",
                   ],
       package_dir={"dimmerattenuation": "src/python"},
       packages=['dimmerattenuation'],
       data_files=[('', ['version.txt'])],
      )
