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

import codecs

class Log(dbus.service.Object):
    def __init__(self, layout):
        self.layout = layout
        self.session_bus = dbus.SessionBus()
        self.name = dbus.service.BusName("org.xmonad.LogService", self.session_bus)
        dbus.service.Object.__init__(self, self.session_bus, '/Log')

    @dbus.service.method(dbus_interface='org.xmonad.Log',
                         in_signature='s', out_signature='')
    def msg(self, msg):
        while self.layout.count() > 0:
            x = self.layout.itemAt(0)
            x.setOwnedByLayout(True)
            self.layout.removeItem(x)

        msg = codecs.decode(msg, 'base64').decode('utf-8')
        for item in msg.split("[[|]]"):
            icon = "konsole"
            color = ""
            font_weight = None
            text_decoration = None

            if "[[t]]" in item:
                self.layout.addItem(HelloPython.getLabel(item.replace("[[t]]", ""), "", font_weight, text_decoration))
                continue
            elif "[[l]]" in item:
                self.layout.addItem(HelloPython.getLabel(item.replace("[[l]]", ""), "", "bold", text_decoration))
                continue
            else:
                if "www" in item:
                    icon = "www-browser"
                if "im" in item:
                    icon = "pidgin"
                if "[[v]]" in item:
                    color = "white"
                    font_weight = "bold"
                    item = item.replace("[[v]]", "")
                if "[[c]]" in item:
                    color = "lightgreen"
                    font_weight = "bold"
                    item = item.replace("[[c]]", "")
                if "[[u]]" in item:
                    color = "yellow"
                    font_weight = "bold"
                    text_decoration = "underline"
                    item = item.replace("[[u]]", "")
                self.layout.addItem(HelloPython.getToolButton(item, icon, color, font_weight, text_decoration))

        for i in range(self.layout.count()):
            self.layout.setAlignment(self.layout.itemAt(i), Qt.AlignVCenter)

 
class HelloPython(plasmascript.Applet):
    def __init__(self, parent, args=None):
        plasmascript.Applet.__init__(self, parent)

    @staticmethod
    def getToolButton(text, icon, color = "#BECFD2", font_weight = "normal", text_decoration = "none"):
        x = Plasma.ToolButton()
        x.setIcon(KIcon(icon))
        x.setText(text)
        x.setContentsMargins(0,0,0,0)
        x.nativeWidget().setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        style_sheet = "QToolButton { color: %s; font-weight: %s; text-decoration: %s; font-size: 11px; max-height: 18px; padding-top: 0; padding-bottom: 0; }" % (color, font_weight, text_decoration)
        x.nativeWidget().setStyleSheet(style_sheet)
        return x

    @staticmethod
    def getLabel(text, color = "#BECFD2", font_weight = "normal", text_decoration = "none"):
        x = Plasma.Label()
        x.setText(text)
        x.setContentsMargins(0,0,0,0)
        x.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum);
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
        self.layout.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)
        self.applet.setLayout(self.layout)

        #self.setMinimumWidth(200)
        self.setMinimumHeight(30)
        
        self.setMaximumHeight(100)
        self.layout.setMaximumHeight(100)

        self.setup_dbus()
 
def CreateApplet(parent):
    DBusQtMainLoop(set_as_default=True)
    return HelloPython(parent)
