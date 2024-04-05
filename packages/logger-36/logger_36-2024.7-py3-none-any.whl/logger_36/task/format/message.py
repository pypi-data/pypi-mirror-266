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

import typing as h

from logger_36.config.message import (
    ELAPSED_TIME_FORMAT,
    LEVEL_CLOSING,
    LEVEL_OPENING,
    MEMORY_FORMAT,
    MESSAGE_MARKER,
)
from logger_36.constant.generic import NOT_PASSED
from logger_36.constant.message import EXPECTED_OP, expected_op_h


def MessageFormat(with_where: bool, with_memory_usage: bool, /) -> str:
    """"""
    output = [
        f"%(asctime)s"
        f"{LEVEL_OPENING}%(level_first_letter)s{LEVEL_CLOSING}\t"
        f"{MESSAGE_MARKER}%(message)s"
    ]

    if with_where:
        output.append("%(where)s")
    output.append(ELAPSED_TIME_FORMAT)
    if with_memory_usage:
        output.append(MEMORY_FORMAT)

    return "".join(output)


def FormattedMessage(
    message: str,
    /,
    *,
    actual: h.Any = NOT_PASSED,
    expected: h.Any | None = None,
    expected_op: expected_op_h = "=",
    with_final_dot: bool = True,
) -> str:
    """"""
    if expected_op not in EXPECTED_OP:
        raise ValueError(
            FormattedMessage(
                'Invalid "expected" section operator',
                actual=expected_op,
                expected=f"One of {str(EXPECTED_OP)[1:-1]}",
            )
        )

    if actual is NOT_PASSED:
        if with_final_dot:
            if message[-1] != ".":
                message += "."
        elif message[-1] == ".":
            message = message[:-1]

        return message

    if message[-1] == ".":
        message = message[:-1]
    actual = _FormattedValue(actual)
    expected = _FormattedValue(expected)

    if with_final_dot:
        dot = "."
    else:
        dot = ""
    return f"{message}: Actual={actual}; Expected{expected_op}{expected}{dot}"


def _FormattedValue(value: h.Any, /, *, should_format_str: bool = True) -> str:
    """"""
    if value is None:
        return "None"

    if isinstance(value, str):
        if should_format_str:
            return f'"{value}"'
        return value

    return str(value)
