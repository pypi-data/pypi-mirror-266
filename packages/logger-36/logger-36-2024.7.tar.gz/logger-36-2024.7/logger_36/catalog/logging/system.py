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

from logger_36.constant.logger import HIDE_WHERE_KWARG
from logger_36.constant.system import MAX_DETAIL_NAME_LENGTH, SYSTEM_DETAILS_AS_DICT
from logger_36.instance import LOGGER
from logger_36.task.inspection import Modules


def LogSystemDetails(
    *,
    modules_with_version: bool = True,
    modules_formatted: bool = True,
    should_restrict_modules_to_loaded: bool = True,
) -> None:
    """"""
    details = "\n".join(
        f"    {_key:>{MAX_DETAIL_NAME_LENGTH}}: {_vle}"
        for _key, _vle in SYSTEM_DETAILS_AS_DICT.items()
    )
    modules = Modules(
        modules_with_version,
        modules_formatted,
        only_loaded=should_restrict_modules_to_loaded,
        indent=4,
    )

    LOGGER.info(
        f"SYSTEM DETAILS\n"
        f"{details}\n"
        f"    {'Python Modules':>{MAX_DETAIL_NAME_LENGTH}}:\n"
        f"{modules}",
        **HIDE_WHERE_KWARG,
    )
