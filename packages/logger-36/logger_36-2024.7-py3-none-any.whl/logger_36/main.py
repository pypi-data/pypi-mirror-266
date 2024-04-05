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

import logging as lggg
import sys as sstm
from pathlib import Path as path_t

try:
    from logger_36.catalog.handler.console_rich import console_rich_handler_t

    _RICH_ERROR = None
except ModuleNotFoundError:
    from logger_36.catalog.handler.console import (
        console_handler_t as console_rich_handler_t,
    )

    _RICH_ERROR = (
        "The Rich console handler is not available, "
        "probably because the Rich package "
        "(https://rich.readthedocs.io/en/stable/index.html) "
        "is not installed, or not loadable. "
        "Falling back to the raw console."
    )
from logger_36.catalog.handler.console import console_handler_t
from logger_36.catalog.handler.file import file_handler_t
from logger_36.catalog.handler.generic import generic_handler_t, interface_h
from logger_36.constant.handler import HANDLER_CODES, handler_codes_h
from logger_36.instance import LOGGER
from logger_36.task.format.message import FormattedMessage


def AddGenericHandler(
    interface: interface_h,
    /,
    *,
    logger: lggg.Logger | None = None,
    name: str | None = None,
    level: int = lggg.INFO,
    show_where: bool = True,
    show_memory_usage: bool = False,
    formatter: lggg.Formatter | None = None,
    supports_html: bool = False,
    should_hold_messages: bool = False,
    **kwargs,
) -> None:
    """"""
    if logger is None:
        logger = LOGGER

    handler = generic_handler_t(
        name=name,
        level=level,
        show_where=show_where,
        show_memory_usage=show_memory_usage,
        formatter=formatter,
        supports_html=supports_html,
        rich_kwargs=kwargs,
        interface=interface,
    )
    logger.AddHandler(handler, should_hold_messages)


def AddConsoleHandler(
    *,
    logger: lggg.Logger | None = None,
    name: str | None = None,
    level: int = lggg.INFO,
    show_where: bool = True,
    show_memory_usage: bool = False,
    formatter: lggg.Formatter | None = None,
    should_hold_messages: bool = False,
) -> None:
    """"""
    if logger is None:
        logger = LOGGER

    handler = console_handler_t(
        name=name,
        level=level,
        show_where=show_where,
        show_memory_usage=show_memory_usage,
        formatter=formatter,
    )
    logger.AddHandler(handler, should_hold_messages)


def AddRichConsoleHandler(
    *,
    logger: lggg.Logger | None = None,
    name: str | None = None,
    level: int = lggg.INFO,
    show_where: bool = True,
    show_memory_usage: bool = False,
    formatter: lggg.Formatter | None = None,
    should_hold_messages: bool = False,
    should_install_traceback: bool = False,
    **kwargs,
) -> None:
    """"""
    global _RICH_ERROR
    if _RICH_ERROR is not None:
        print(_RICH_ERROR, file=sstm.stderr)
        _RICH_ERROR = None

    if logger is None:
        logger = LOGGER

    handler = console_rich_handler_t(
        name=name,
        level=level,
        show_where=show_where,
        show_memory_usage=show_memory_usage,
        formatter=formatter,
        should_install_traceback=should_install_traceback,
        rich_kwargs=kwargs,
    )
    logger.AddHandler(handler, should_hold_messages)


def AddFileHandler(
    path: str | path_t,
    /,
    *args,
    logger: lggg.Logger | None = None,
    name: str | None = None,
    level: int = lggg.INFO,
    show_where: bool = True,
    show_memory_usage: bool = False,
    formatter: lggg.Formatter | None = None,
    should_hold_messages: bool = False,
    **kwargs,
) -> None:
    """"""
    if isinstance(path, str):
        path = path_t(path)
    if path.exists():
        raise ValueError(f"File or folder already exists: {path}.")
    if logger is None:
        logger = LOGGER

    handler = file_handler_t(
        name=name,
        level=level,
        show_where=show_where,
        show_memory_usage=show_memory_usage,
        formatter=formatter,
        path=path,
        handler_args=args,
        handler_kwargs=kwargs,
    )
    logger.AddHandler(handler, should_hold_messages)


def SetLOGLevel(
    level: int,
    /,
    *,
    logger: lggg.Logger | None = None,
    which: handler_codes_h | str = "a",
) -> None:
    """
    which: g=generic, c=console, f=file, a=all, str=name.
    """
    if logger is None:
        logger = LOGGER

    which_is_name = which not in HANDLER_CODES
    found = False
    for handler in logger.handlers:
        if (
            (which == "a")
            or ((which == "g") and isinstance(handler, generic_handler_t))
            or (
                (which == "c")
                and isinstance(handler, (console_handler_t, console_rich_handler_t))
            )
            or ((which == "f") and isinstance(handler, file_handler_t))
            or (which == handler.name)
        ):
            handler.setLevel(level)
            if which_is_name:
                return
            found = True

    if not found:
        raise ValueError(
            FormattedMessage(
                "Handler not found",
                actual=which,
                expected=f"{str(HANDLER_CODES)[1:-1]}, or a handler name",
            )
        )
