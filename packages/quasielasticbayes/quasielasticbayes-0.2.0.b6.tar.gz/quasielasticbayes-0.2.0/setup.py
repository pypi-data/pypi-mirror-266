"""
Setuptools support for building the Fortran extensions with
numpy.f2py
"""
from os import environ
from pathlib import PurePosixPath
# Importing setuptools modifies the behaviour of setup from distutils
# to support building wheels. It will be marked as unused by IDEs/static analysis.
import setuptools
import sys
from typing import Sequence

from numpy.distutils.core import (Extension as FortranExtension, setup)
from numpy.distutils.command.build_ext import build_ext as _build_ext

PACKAGE_NAME = 'quasielasticbayes'


def create_fortran_extension(fq_name: str, sources: Sequence[str]) -> FortranExtension:
    """
    Create an extension module to be built by f2py
    :param fq_name: The final fully-qualified name of the module
    :param sources: List of relative paths from this file to the sources
    :return: An Extension class to be built
    """
    _remove_environment_compiler_flags()
    return FortranExtension(name=fq_name,
                            sources=sources,
                            extra_f90_compile_args=["-O1", "-std=legacy"],
                            extra_link_args=["-static", "-static-libgfortran", "-static-libgcc"]
                                             if sys.platform == "win32" else [])


def _remove_environment_compiler_flags() -> None:
    """
    Using the 'gfortran_linux-64' and 'gfortran_osx-64' conda packages gives poor fit results by default 
    because they set several optimization compiler flags which alter the operation of the Fortran code. We 
    must therefore remove these flags from the 'FFLAGS' environment variable before performing the compilation.
    """
    fflags_value = environ.get('FFLAGS')
    if isinstance(fflags_value, str):
        fflags_value = fflags_value.replace("-fstack-protector ", "")
        fflags_value = fflags_value.replace("-fstack-protector-strong ", "")
        environ['FFLAGS'] = fflags_value


def source_paths(dirname: PurePosixPath, filenames: Sequence[str]) -> Sequence[str]:
    """
    :param dirname: A relative path to the list of source files
    :return: A list of relative paths to the given sources in the directory
    """
    return [str(dirname / filename) for filename in filenames]


class FortranExtensionBuilder(_build_ext):
    """Custom extension builder to use specific compilers"""

    def finalize_options(self):
        _build_ext.finalize_options(self)
        # If we don't do this on windows, when we do bdist_wheel we wont get a static link
        # this is because it misses the compiler flags to f2py which means it ignores the static flags we try to pass
        if sys.platform == 'win32':
            self.fcompiler = 'gnu95'
            self.compiler = 'mingw32'


# Start setup
# Create extension builders
module_source_map = {
    f'{PACKAGE_NAME}.ResNorm': ['ResNorm_main.f90',
                                'ResNorm_subs.f90',
                                'BlrRes.f90',
                                'Bayes.f90',
                                'Four.f90',
                                'Util.f90'],
    f'{PACKAGE_NAME}.Quest': ['Quest_main.f90',
                              'Quest_subs.f90',
                              'BlrRes.f90',
                              'Bayes.f90',
                              'Four.f90',
                              'Util.f90',
                              'Simopt.f90'],
    f'{PACKAGE_NAME}.QLse':
        ['QLse_main.f90',
         'QLse_subs.f90',
         'BlrRes.f90',
         'Bayes.f90',
         'Four.f90',
         'Util.f90',
         'Simopt.f90'],
    f'{PACKAGE_NAME}.QLres':
        ['QLres_main.f90',
         'QLres_subs.f90',
         'BlrRes.f90',
         'Bayes.f90',
         'Four.f90',
         'Util.f90'],
    f'{PACKAGE_NAME}.QLdata': ['QLdata_main.f90',
                               'QLdata_subs.f90',
                               'Bayes.f90',
                               'Four.f90',
                               'Util.f90'],
    f'{PACKAGE_NAME}.Four':
            ['Four_main.f90',
             'Four.f90'],
}
extensions = [create_fortran_extension(name, source_paths(PurePosixPath('quasielasticbayes'), sources)) for
              name, sources in module_source_map.items()]

setup(
    name=PACKAGE_NAME,
    packages=[PACKAGE_NAME],
    description="A Bayesian fitting package used for fitting quasi-elastic neutron scattering (QENS) data.",
    long_description="This package wraps Fortran Bayesian fitting libraries using f2py. "
                     "An application of this package is to fit QENS data in Mantid (https://www.mantidproject.org).",
    author="Dr. Devinder Sivia, Dr. Spencer Howells, Mantid Team",
    ext_modules=extensions,
    author_email="mantid-help@mantidproject.org",
    url="https://github.com/mantidproject/quasielasticbayes",
    version="0.2.0",
    license="BSD",
    cmdclass={"build_ext": FortranExtensionBuilder}
)
