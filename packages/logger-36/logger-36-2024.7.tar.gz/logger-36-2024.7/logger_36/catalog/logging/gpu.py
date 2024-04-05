# Copyright CNRS/Inria/UCA
# Contributor(s): Eric Debreuve (since 2023)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from logger_36.constant.handler import HIDE_WHERE_KWARG
from logger_36.instance import LOGGER

try:
    import tensorflow as tsfl
    import tensorrt as tsrt
except ModuleNotFoundError:
    tsfl = tsrt = None


def LogGPURelatedDetails() -> None:
    """"""
    if None in (tsfl, tsrt):
        return

    system_details = tsfl.sysconfig.get_build_info()
    LOGGER.info(
        f"GPU-RELATED DETAILS\n"
        f"                GPUs: {tsfl.config.list_physical_devices('GPU')}\n"
        f"                CPUs: {tsfl.config.list_physical_devices('CPU')}\n"
        f"                Cuda: {system_details['cuda_version']}\n"
        f"               CuDNN: {system_details['cudnn_version']}\n"
        f"          Tensorflow: {tsfl.version.VERSION}\n"
        f"    Tensorflow Build: {tsfl.sysconfig.get_build_info()}\n"
        f"            TensorRT: {tsrt.__version__}",
        **HIDE_WHERE_KWARG,
    )
