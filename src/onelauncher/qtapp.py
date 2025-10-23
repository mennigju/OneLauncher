###########################################################################
# Runner for OneLauncher.
#
# Based on PyLotRO
# (C) 2009 AJackson <ajackson@bcs.org.uk>
#
# Based on LotROLinux
# (C) 2007-2008 AJackson <ajackson@bcs.org.uk>
#
#
# (C) 2019-2025 June Stepp <contact@JuneStepp.me>
#
# This file is part of OneLauncher
#
# OneLauncher is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# OneLauncher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OneLauncher.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
import os
import sys
import shutil
import subprocess
from functools import cache
from pathlib import Path

import qtawesome
from PySide6 import QtCore, QtGui, QtWidgets

from onelauncher.ui.style import ApplicationStyle

from .__about__ import __title__, __version__
from .resources import data_dir


@cache
def _setup_qapplication() -> QtWidgets.QApplication:
    application = QtWidgets.QApplication(sys.argv)
    # See https://github.com/zhiyiYo/PyQt-Frameless-Window/issues/50
    application.setAttribute(
        QtCore.Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings
    )
    # Will be quit after Trio event loop finishes
    application.setQuitOnLastWindowClosed(False)
    application.setApplicationName(__title__)
    application.setApplicationDisplayName(__title__)
    application.setApplicationVersion(__version__)
    application.setWindowIcon(
        QtGui.QIcon(
            str(
                data_dir / Path("images/OneLauncherIcon.png"),
            )
        )
    )

    # The Qt "Windows" style doesn't work with dark mode
    if os.name == "nt":
        application.setStyle("Fusion")

    def _gnome_prefers_dark() -> bool:
        # Simple heuristics for GNOME dark preference when Qt portal support is missing
        try:
            gtk_theme = os.environ.get("GTK_THEME", "")
            if gtk_theme and "dark" in gtk_theme.lower():
                return True
            if shutil.which("gsettings"):
                # GNOME 42+: color-scheme key
                result = subprocess.run(
                    [
                        "gsettings",
                        "get",
                        "org.gnome.desktop.interface",
                        "color-scheme",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=0.6,
                )
                if result.returncode == 0 and "prefer-dark" in result.stdout:
                    return True
                # Fallback to theme name check
                result = subprocess.run(
                    [
                        "gsettings",
                        "get",
                        "org.gnome.desktop.interface",
                        "gtk-theme",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=0.6,
                )
                if result.returncode == 0 and "dark" in result.stdout.lower():
                    return True
        except Exception:
            pass
        return False

    def _apply_fusion_dark_palette(app: QtWidgets.QApplication) -> None:
        # Ensure a style that respects palette
        app.setStyle("Fusion")
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(
            QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("white")
        )
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(42, 42, 42))
        palette.setColor(
            QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(66, 66, 66)
        )
        palette.setColor(
            QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor("white")
        )
        palette.setColor(
            QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor("white")
        )
        palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("white"))
        palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(
            QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("white")
        )
        palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor("red"))
        palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(
            QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218)
        )
        palette.setColor(
            QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor("black")
        )
        app.setPalette(palette)

    def set_qtawesome_defaults() -> None:
        qtawesome.reset_cache()
        qtawesome.set_defaults(color=application.palette().windowText().color())

    # Workaround: Some GNOME setups don’t expose dark preference to Qt. Apply dark palette if we detect it.
    try:
        if sys.platform.startswith("linux"):
            cs = application.styleHints().colorScheme()
            if cs == QtCore.Qt.ColorScheme.Light and _gnome_prefers_dark():
                _apply_fusion_dark_palette(application)
    except Exception:
        # Never allow theme workaround to break startup
        pass

    set_qtawesome_defaults()
    application.styleHints().colorSchemeChanged.connect(set_qtawesome_defaults)

    return application


@cache
def get_qapp() -> QtWidgets.QApplication:
    application = _setup_qapplication()
    # Setup ApplicationStyle
    _ = get_app_style()
    return application


@cache
def get_app_style() -> ApplicationStyle:
    return ApplicationStyle(_setup_qapplication())
