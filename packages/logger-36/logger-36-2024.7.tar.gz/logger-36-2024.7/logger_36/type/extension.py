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
import sys as sstm
import typing as h

from logger_36.config.message import TIME_FORMAT, WHERE_FORMAT
from logger_36.constant.handler import HANDLER_CODES
from logger_36.constant.memory import MEMORY_MEASURE_ERROR
from logger_36.constant.message import NEXT_LINE_PROLOGUE
from logger_36.constant.record import HIDE_WHERE_ATTR, SHOW_WHERE_ATTR
from logger_36.task.format.message import FormattedMessage, MessageFormat
from logger_36.task.measure.chronos import TimeStamp
from logger_36.task.measure.memory import CanCheckMemory


@dtcl.dataclass(slots=True, repr=False, eq=False)
class handler_extension_t:
    name: str | None = None
    show_where: bool = True
    show_memory_usage: bool = False
    FormattedRecord: h.Callable[[lggg.LogRecord], str] = dtcl.field(init=False)

    handler: dtcl.InitVar[lggg.Handler | None] = None
    level: dtcl.InitVar[int] = lggg.NOTSET
    formatter: dtcl.InitVar[lggg.Formatter | None] = None

    def __post_init__(
        self, handler: lggg.Handler | None, level: int, formatter: lggg.Formatter | None
    ) -> None:
        """"""
        if self.name in HANDLER_CODES:
            raise ValueError(
                FormattedMessage(
                    "Invalid handler name",
                    actual=self.name,
                    expected=f"a name not in {str(HANDLER_CODES)[1:-1]}",
                )
            )

        if self.name is None:
            self.name = TimeStamp()

        if self.show_memory_usage and not CanCheckMemory():
            self.show_memory_usage = False
            print(MEMORY_MEASURE_ERROR, file=sstm.stderr)

        handler.setLevel(level)

        if formatter is None:
            message_format = MessageFormat(self.show_where, self.show_memory_usage)
            formatter = lggg.Formatter(fmt=message_format, datefmt=TIME_FORMAT)
        handler.setFormatter(formatter)
        self.FormattedRecord = handler.formatter.format

    def FormattedLines(
        self,
        record: lggg.LogRecord,
        /,
        *,
        PreProcessed: h.Callable[[str], str] | None = None,
        should_join_lines: bool = False,
    ) -> tuple[str, str | None]:
        """
        See logger_36.catalog.handler.README.txt.
        """
        record.level_first_letter = record.levelname[0]

        message = record.msg
        if not isinstance(message, str):
            message = str(message)
        original_message = message

        if PreProcessed is not None:
            message = PreProcessed(message)
        if "\n" in message:
            lines = message.splitlines()
            next_lines = NEXT_LINE_PROLOGUE.join(lines[1:])
            next_lines = f"{NEXT_LINE_PROLOGUE}{next_lines}"
            message = lines[0]
        else:
            next_lines = None

        record.msg = message
        if self.show_where and not hasattr(record, SHOW_WHERE_ATTR):
            hide_where = getattr(record, HIDE_WHERE_ATTR, False)
            if hide_where:
                record.where = ""
            else:
                record.where = WHERE_FORMAT.format(
                    module=record.module, funcName=record.funcName, lineno=record.lineno
                )
        first_line = self.FormattedRecord(record).replace("\t", " ")

        # Revert the record message to its original value for subsequent handlers.
        record.msg = original_message

        if should_join_lines:
            if next_lines is None:
                return first_line, None
            else:
                return f"{first_line}{next_lines}", None
        else:
            return first_line, next_lines
