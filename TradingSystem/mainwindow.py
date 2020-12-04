
from typing import Callable
import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import ctypes
import platform
import sys
import traceback
from gateway import Gateway
import qdarkstyle
from PyQt5 import QtGui, QtWidgets, QtCore
from constant import Direction, Exchange,  OrderType
from event import EventEngine
from widget import (
    TickMonitor,
    TradeMonitor,
    PositionMonitor,
    TradingWidget
)
from engine import MainEngine
from utility import get_icon_path


class MainWindow(QtWidgets.QMainWindow):


    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super(MainWindow, self).__init__()
        self.main_engine = main_engine
        self.event_engine = event_engine

        self.window_title = "My trading system"

        self.connect_dialogs = {}
        self.widgets = {}

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle(self.window_title)
        self.init_dock()
        self.init_menu()
        self.load_window_setting("custom")

    def init_dock(self):
        """"""
        self.trading_widget, trading_dock = self.create_dock(
            TradingWidget, "Trade", QtCore.Qt.LeftDockWidgetArea
        )
        tick_widget, tick_dock = self.create_dock(
            TickMonitor, "stock data", QtCore.Qt.RightDockWidgetArea
        )


        trade_widget, trade_dock = self.create_dock(
            TradeMonitor, "trade", QtCore.Qt.RightDockWidgetArea
        )

        position_widget, position_dock = self.create_dock(
            PositionMonitor, "position", QtCore.Qt.BottomDockWidgetArea
        )


    def connect(self):
        gateway=Gateway(self.event_engine,'AAPL',Exchange.NYMEX)

        gateway.generate_Tick()


    def init_menu(self):
        """"""
        bar = self.menuBar()

        # System menu
        sys_menu = bar.addMenu("system")

        # for name in gateway_names:
        #     func = partial(self.connect, name)
        self.add_menu_action(sys_menu, "connect", "connect.ico", self.connect)

        sys_menu.addSeparator()

        self.add_menu_action(sys_menu, "exit", "exit.ico", self.close)



    def add_menu_action(
        self,
        menu: QtWidgets.QMenu,
        action_name: str,
        icon_name: str,
        func: Callable,
    ):
        """"""
        icon = QtGui.QIcon(get_icon_path(__file__, icon_name))

        action = QtWidgets.QAction(action_name, self)
        action.triggered.connect(func)
        action.setIcon(icon)

        menu.addAction(action)

    def add_toolbar_action(
        self,
        action_name: str,
        icon_name: str,
        func: Callable,
    ):
        """"""
        icon = QtGui.QIcon(get_icon_path(__file__, icon_name))

        action = QtWidgets.QAction(action_name, self)
        action.triggered.connect(func)
        action.setIcon(icon)

        self.toolbar.addAction(action)

    def create_dock(
        self, widget_class: QtWidgets.QWidget, name: str, area: int
    ):
        """
        Initialize a dock widget.
        """
        widget = widget_class(self.main_engine, self.event_engine)

        dock = QtWidgets.QDockWidget(name)
        dock.setWidget(widget)
        dock.setObjectName(name)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)
        self.addDockWidget(area, dock)
        return widget, dock



    def closeEvent(self, event):
        """
        Call main engine close function before exit.
        """
        reply = QtWidgets.QMessageBox.question(
            self,
            "exit",
            "Are you sure？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )

        if reply == QtWidgets.QMessageBox.Yes:
            for widget in self.widgets.values():
                widget.close()
            self.main_engine.close()

            event.accept()
        else:
            event.ignore()

    def open_widget(self, widget_class: QtWidgets.QWidget, name: str):
        """
        Open contract manager.
        """
        widget = self.widgets.get(name, None)
        if not widget:
            widget = widget_class(self.main_engine, self.event_engine)
            self.widgets[name] = widget

        if isinstance(widget, QtWidgets.QDialog):
            widget.exec_()
        else:
            widget.show()

    def load_window_setting(self, name: str):
        """
        Load previous window size and state by trader path and setting name.
        """
        settings = QtCore.QSettings(self.window_title, name)
        state = settings.value("state")
        geometry = settings.value("geometry")

        if isinstance(state, QtCore.QByteArray):
            self.restoreState(state)
            self.restoreGeometry(geometry)

    def restore_window_setting(self):
        """
        Restore window to default setting.
        """
        self.load_window_setting("default")
        self.showMaximized()


def excepthook(exctype, value, tb):
    """
    Raise exception under debug mode, otherwise
    show exception detail with QMessageBox.
    """
    sys.__excepthook__(exctype, value, tb)

    msg = "".join(traceback.format_exception(exctype, value, tb))
    QtWidgets.QMessageBox.critical(
        None, "Exception", msg, QtWidgets.QMessageBox.Ok
    )


def create_qapp(app_name):
    """
    Create Qt Application.
    """
    sys.excepthook = excepthook

    qapp = QtWidgets.QApplication([])
    qapp.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    if "Windows" in platform.uname():
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            app_name
        )

    return qapp