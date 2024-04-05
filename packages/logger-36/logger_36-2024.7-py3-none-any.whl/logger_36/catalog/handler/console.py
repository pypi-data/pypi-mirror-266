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

import dataclasses as dtcl
import logging as lggg
import typing as h

from logger_36.constant.record import SHOW_W_RULE_ATTR
from logger_36.task.format.rule import RuleAsText
from logger_36.type.extension import handler_extension_t


@dtcl.dataclass(slots=True, repr=False, eq=False)
class console_handler_t(lggg.Handler):
    extension: handler_extension_t = dtcl.field(init=False)
    FormattedLines: h.Callable[..., tuple[str, str | None]] = dtcl.field(init=False)

    name: dtcl.InitVar[str | None] = None
    level: dtcl.InitVar[int] = lggg.NOTSET
    show_where: dtcl.InitVar[bool] = True
    show_memory_usage: dtcl.InitVar[bool] = False
    formatter: dtcl.InitVar[lggg.Formatter | None] = None

    def __post_init__(
        self,
        name: str | None,
        level: int,
        show_where: bool,
        show_memory_usage: bool,
        formatter: lggg.Formatter | None,
    ) -> None:
        """"""
        lggg.Handler.__init__(self)

        self.extension = handler_extension_t(
            name=name,
            show_where=show_where,
            show_memory_usage=show_memory_usage,
            handler=self,
            level=level,
            formatter=formatter,
        )

        self.FormattedLines = self.extension.FormattedLines

    def emit(self, record: lggg.LogRecord, /) -> None:
        """"""
        if hasattr(record, SHOW_W_RULE_ATTR):
            message = RuleAsText(record.msg)
        else:
            message, _ = self.FormattedLines(record, should_join_lines=True)
        print(message)
