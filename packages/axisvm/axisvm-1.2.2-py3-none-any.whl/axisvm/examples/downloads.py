"""Downloadable datasets collected from various sources.

Once downloaded, these datasets are stored locally allowing for the
rapid reuse of these datasets.

Examples
--------
>>> from axisvm.com.client import start_AxisVM
>>> from axisvm import examples
>>> axvm = start_AxisVM(visible=True, daemon=True)
>>> axvm.model = examples.download_bernoulli_grid()

"""

from functools import partial
import os
import shutil
from urllib.request import urlretrieve
import zipfile

import axisvm

import pyvista


def _check_examples_path():
    """Check if the examples path exists."""
    if not axisvm.EXAMPLES_PATH:
        raise FileNotFoundError(
            "EXAMPLES_PATH does not exist.  Try setting the "
            "environment variable `AXISVM_USERDATA_PATH` "
            "to a writable path and restarting python"
        )


def delete_downloads():
    """Delete all downloaded examples to free space or update the files.

    Returns
    -------
    bool
        Returns ``True``.

    Examples
    --------
    Delete all local downloads.

    >>> from axisvm import examples
    >>> axisvm.delete_downloads()  # doctest:+SKIP
    True

    """
    _check_examples_path()
    shutil.rmtree(axisvm.EXAMPLES_PATH)
    os.makedirs(axisvm.EXAMPLES_PATH)
    return True


def _decompress(filename):
    _check_examples_path()
    zip_ref = zipfile.ZipFile(filename, "r")
    zip_ref.extractall(axisvm.EXAMPLES_PATH)
    return zip_ref.close()


def _get_vtk_file_url(filename):
    return f"https://github.com/AxisVM/axisvm-data/raw/main/{filename}"


def _http_request(url):
    return urlretrieve(url)


def _repo_file_request(repo_path, filename):
    return os.path.join(repo_path, "Data", filename), None


def _retrieve_file(retriever, filename):
    """Retrieve file and cache it in pyvsita.EXAMPLES_PATH.

    Parameters
    ----------
    retriever : str or callable
        If str, it is treated as a url.
        If callable, the function must take no arguments and must
        return a tuple like (file_path, resp), where file_path is
        the path to the file to use.
    filename : str
        The name of the file.
    """
    _check_examples_path()
    # First check if file has already been downloaded
    local_path = os.path.join(axisvm.EXAMPLES_PATH, os.path.basename(filename))
    local_path_no_zip = local_path.replace(".zip", "")
    if os.path.isfile(local_path_no_zip) or os.path.isdir(local_path_no_zip):
        return local_path_no_zip, None
    if isinstance(retriever, str):
        retriever = partial(_http_request, retriever)
    saved_file, resp = retriever()
    # new_name = saved_file.replace(os.path.basename(saved_file), os.path.basename(filename))
    # Make sure folder exists!
    if not os.path.isdir(os.path.dirname((local_path))):
        os.makedirs(os.path.dirname((local_path)))
    if axisvm.AXISVM_DATA_PATH is None:
        shutil.move(saved_file, local_path)
    else:
        if os.path.isdir(saved_file):
            shutil.copytree(saved_file, local_path)
        else:
            shutil.copy(saved_file, local_path)
    if pyvista.get_ext(local_path) in [".zip"]:
        _decompress(local_path)
        local_path = local_path[:-4]
    return local_path, resp


def _download_file(filename):
    if axisvm.AXISVM_DATA_PATH is None:
        url = _get_vtk_file_url(filename)
        retriever = partial(_http_request, url)
    else:
        if not os.path.isdir(axisvm.AXISVM_DATA_PATH):
            raise FileNotFoundError(
                f"VTK data repository path does not exist at:\n\n{axisvm.AXISVM_DATA_PATH}"
            )
        if not os.path.isdir(os.path.join(axisvm.AXISVM_DATA_PATH, "Data")):
            raise FileNotFoundError(
                f'VTK data repository does not have "Data" folder at:\n\n{axisvm.AXISVM_DATA_PATH}'
            )
        retriever = partial(_repo_file_request, axisvm.AXISVM_DATA_PATH, filename)
    return _retrieve_file(retriever, filename)


def _download_and_read(filename):
    saved_file, _ = _download_file(filename)
    return saved_file


###############################################################################


def download_tetrahedra():  # pragma: no cover
    """
    Downloads an AxisVM model file with a grid of beams.

    Returns
    -------
    str
        A path to an AxisVM model file on your filesystem.

    Example
    --------
    >>> from axisvm.com.client import start_AxisVM
    >>> from axisvm import examples
    >>> axvm = start_AxisVM(visible=True, daemon=True)
    >>> axvm.model = examples.download_tetrahedra()

    """
    return _download_and_read("tetrahedra_vX5r4.axs")


def download_bernoulli_grid():  # pragma: no cover
    """
    Downloads an AxisVM model file with a grid of beams.

    Returns
    -------
    str
        A path to an AxisVM model file on your filesystem.
        
    Note
    ----
    You need AxisVM version X5r4 or later to open this file.

    Example
    --------
    >>> from axisvm.com.client import start_AxisVM
    >>> from axisvm import examples
    >>> axvm = start_AxisVM(visible=True, daemon=True)
    >>> axvm.model = examples.download_bernoulli_grid()

    """
    return _download_and_read("console_H8_L2_vX5r4.axs")


def download_stem_stl():  # pragma: no cover
    """
    Downloads an stl file describing a stem.

    Returns
    -------
    str
        A path to an stl file on your filesystem.

    Example
    --------
    >>> from axisvm import examples
    >>> examples.download_stem_stl()

    """
    return _download_and_read("stem.stl")


def download_stand_vtk():  # pragma: no cover
    """
    Downloads a vtk file describing a stem.

    Returns
    -------
    str
        A path to a vtk file on your filesystem.

    Example
    --------
    >>> from axisvm import examples
    >>> examples.download_stand_vtk()

    """
    return _download_and_read("stand.vtk")


def download_stand_stl():  # pragma: no cover
    """
    Downloads an stl file describing a simple stand.

    Returns
    -------
    str
        A path to an stl file on your filesystem.

    Example
    --------
    >>> from axisvm import examples
    >>> examples.download_stand_stl()

    """
    return _download_and_read("stand.stl")


def download_sample_001():  # pragma: no cover
    """
    Downloads an AxisVM model with a few beams, trusses and
    domains.

    Returns
    -------
    str
        A path to an AxisVM model file on your filesystem.

    Example
    --------
    >>> from axisvm.com.client import start_AxisVM
    >>> from axisvm import examples
    >>> axvm = start_AxisVM(visible=True, daemon=True)
    >>> axvm.model = examples.download_sample_001()

    """
    return _download_and_read("sample_001.axs")


def download_plate_ss():  # pragma: no cover
    """
    Downloads an AxisVM model with a few beams, trusses and
    domains.

    Returns
    -------
    str
        A path to an AxisVM model file on your filesystem.

    Example
    --------
    >>> from axisvm.com.client import start_AxisVM
    >>> from axisvm import examples
    >>> axvm = start_AxisVM(visible=True, daemon=True)
    >>> axvm.model = examples.download_plate_ss()

    """
    return _download_and_read("ss_plate_vX5r4.axs")
