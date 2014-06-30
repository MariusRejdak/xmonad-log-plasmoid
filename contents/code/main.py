# -*- coding: utf-8 -*-
# <Copyright and license information goes here.>
from PyQt4.QtCore import Qt, pyqtSignal, QObject, QString
from PyQt4.QtGui import QGraphicsLinearLayout, QSizePolicy, QIcon
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon
from PyKDE4 import plasmascript

import dbus
import dbus.service
from dbus.mainloop.qt import DBusQtMainLoop

from multiprocessing import Lock
import codecs


class Log(dbus.service.Object):
    def __init__(self, layout):
        self.layout = layout
        self.mutex = Lock()
        self.session_bus = dbus.SessionBus()
        self.name = dbus.service.BusName("org.xmonad.LogService", self.session_bus)
        dbus.service.Object.__init__(self, self.session_bus, '/Log')

        self.desktops = []
        self.layout_label = XMonadLogPlasmoid.getLabel("...", "#44454A", "bold", None)
        self.layout.addItem(self.layout_label)
        self.layout.setAlignment(self.layout_label, Qt.AlignVCenter)
        self.title_label = XMonadLogPlasmoid.getLabel("Waiting for XMonad", "#44454A", None, None)
        self.layout.addItem(self.title_label)
        self.layout.setAlignment(self.title_label, Qt.AlignVCenter)

    @dbus.service.method(dbus_interface='org.xmonad.Log',
                         in_signature='s', out_signature='')
    def msg(self, msg):
        with self.mutex:
            msg = codecs.decode(msg, 'base64').decode('utf-8')
            title_changed = False
            counter = 0

            for item in msg.split("[[|]]"):
                if "[[t]]" in item:
                    self.title_label.setText(item.replace("[[t]]", ""))
                    title_changed = True
                    continue
                elif "[[l]]" in item:
                    self.layout_label.setText(item.replace("[[l]]", ""))
                    continue
                else:
                    icon = "kcmkwm"
                    color = "#44454A"
                    font_weight = None
                    text_decoration = None

                    if "www" in item:
                        icon = "chromium"
                    if "im1" in item:
                        icon = "pidgin"
                    if "im2" in item:
                        icon = "meeting-participant"
                    if "subl" in item:
                        icon = "sublime-text"
                    if "fm" in item:
                        icon = "user-home"
                    if "misc" in item:
                        icon = "konsole"
                    if "mail" in item:
                        icon = "kontact"
                    if "video" in item:
                        icon = "video-player"
                    if "[[v]]" in item:
                        font_weight = "bold"
                        item = item.replace("[[v]]", "")
                    if "[[c]]" in item:
                        color = "#000000"
                        font_weight = "bold"
                        item = item.replace("[[c]]", "")
                    if "[[u]]" in item:
                        icon = "task-attention"
                        color = "#8B0000"
                        font_weight = "bold"
                        text_decoration = "underline"
                        item = item.replace("[[u]]", "")

                    if counter > len(self.desktops)-1:
                        self.desktops.append(XMonadLogPlasmoid.getToolButton())
                        XMonadLogPlasmoid.setToolButtonStyle(self.desktops[counter], item, icon, color, font_weight, text_decoration)
                        self.layout.insertItem(counter, self.desktops[counter])
                        self.layout.setAlignment(self.desktops[counter], Qt.AlignVCenter)
                    else:
                        XMonadLogPlasmoid.setToolButtonStyle(self.desktops[counter], item, icon, color, font_weight, text_decoration)

                    counter += 1

            if not title_changed:
                self.title_label.setText("")
                title_changed = True

            while counter < len(self.desktops):
                self.desktops[counter].setOwnedByLayout(True)
                self.layout.removeItem(self.desktops[counter])
                del self.desktops[counter]


class XMonadLogPlasmoid(plasmascript.Applet):
    def __init__(self, parent, args=None):
        plasmascript.Applet.__init__(self, parent)

    @staticmethod
    def getToolButton():
        x = Plasma.ToolButton()
        x.setContentsMargins(0, 0, 0, 0)
        x.nativeWidget().setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        return x

    @staticmethod
    def setToolButtonStyle(x, text, icon, color="#383838", font_weight="normal", text_decoration="none"):
        x.setIcon(KIcon(icon))
        x.setText(text)
        style_sheet = "QToolButton { color: %s; font-weight: %s; text-decoration: %s; font-size: 11px; max-height: 18px; padding-top: 0; padding-bottom: 0; }" % (color, font_weight, text_decoration)
        x.nativeWidget().setStyleSheet(style_sheet)

    @staticmethod
    def getLabel(text, color="#383838", font_weight="normal", text_decoration="none"):
        x = Plasma.Label()
        x.setText(text)
        x.setContentsMargins(0, 0, 0, 0)
        x.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        x.setWordWrap(False)
        style_sheet = "QLabel { color: %s; font-weight: %s; text-decoration: %s; font-size: 11px; max-height: 20px; padding-left: 6px }" % (color, font_weight, text_decoration)
        x.nativeWidget().setStyleSheet(style_sheet)
        return x

    def setup_dbus(self):
        self.log = Log(self.layout)

    def init(self):
        global label
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.applet.setLayout(self.layout)

        self.setMinimumHeight(30)
        self.setMaximumHeight(100)
        self.setMaximumWidth(900)
        self.layout.setMaximumHeight(100)

        self.setup_dbus()


def CreateApplet(parent):
    DBusQtMainLoop(set_as_default=True)
    return XMonadLogPlasmoid(parent)
