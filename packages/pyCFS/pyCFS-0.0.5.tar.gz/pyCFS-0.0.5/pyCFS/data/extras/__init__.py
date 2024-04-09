"""
pyCFS.data.extras

Libraries to read and write data in from various formats
"""

import importlib.util

if importlib.util.find_spec("ansys") is not None:
    from . import ansys_io  # noqa
    from . import ansys_to_cfs_element_types  # noqa
if importlib.util.find_spec("vtk") is not None:
    from . import ensight_io  # noqa
    from . import vtk_to_cfs_element_types  # noqa
    from . import vtk_types  # noqa
from . import nihu_io  # noqa
from . import nihu_to_cfs_element_types  # noqa
from . import psv_io  # noqa
