# Copyright 2022 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

from importlib.metadata import version as pkgver

def version() -> str:
    """
    Grabs the current version of the validation package.

    Parameters
    ----------
        None

    Returns
    -------
        version: str
            The current version of the validator package.

    Raises
    ------
        None
    """
    try:
        return pkgver('deepview-validator')
    except Exception:
        from subprocess import Popen, PIPE
        from re import sub
        pipe = Popen('git describe --tags --always', stdout=PIPE, shell=True)
        ver = str(pipe.communicate()[0].rstrip().decode("utf-8"))
        ver = str(sub(r'-g\w+', '', ver))
        return ver.replace('-', '.post')
    