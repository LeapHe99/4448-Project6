
import csv
from enum import Enum
from typing import Any
from copy import copy

from PyQt5 import QtCore, QtGui, QtWidgets

from event import Event, EventEngine
from constant import Direction, Exchange, OrderType
from engine import MainEngine
from event import (
    EVENT_TICK,
    EVENT_TRADE,
    EVENT_ORDER,
    EVENT_POSITION,
    EVENT_ACCOUNT,
)
from object import OrderRequest, SubscribeRequest

import time

COLOR_LONG = QtGui.QColor("red")
COLOR_SHORT = QtGui.QColor("green")
COLOR_BID = QtGui.QColor(255, 174, 201)
COLOR_ASK = QtGui.QColor(160, 255, 160)
COLOR_BLACK = QtGui.QColor("black")


class BaseCell(QtWidgets.QTableWidgetItem):
    """
    General cell used in tablewidgets.
    """

    def __init__(self, content: Any, data: Any):
        """"""
        super(BaseCell, self).__init__()
        self.setTextAlignment(QtCore.Qt.AlignCenter)
        self.set_content(content, data)

    def set_content(self, content: Any, data: Any):
        """
        Set text content.
        """
        self.setText(str(content))
        self._data = data

    def get_data(self):
        """
        Get data object.
        """
        return self._data


class EnumCell(BaseCell):
    """
    Cell used for showing enum data.
    """

    def __init__(self, content: str, data: Any):
        """"""
        super(EnumCell, self).__init__(content, data)

    def set_content(self, content: Any, data: Any):
        """
        Set text using enum.constant.value.
        """
        if content:

            super(EnumCell, self).set_content(content.value, data)


class DirectionCell(EnumCell):
    """
    Cell used for showing direction data.
    """

    def __init__(self, content: str, data: Any):
        """"""
        super(DirectionCell, self).__init__(content, data)

    def set_content(self, content: Any, data: Any):
        """
        Cell color is set according to direction.
        """
        super(DirectionCell, self).set_content(content, data)

        if content is Direction.SHORT:
            self.setForeground(COLOR_SHORT)
        else:
            self.setForeground(COLOR_LONG)


class BidCell(BaseCell):
    """
    Cell used for showing bid price and volume.
    """

    def __init__(self, content: Any, data: Any):
        """"""
        super(BidCell, self).__init__(content, data)

        self.setForeground(COLOR_BLACK)
        self.setForeground(COLOR_BID)


class AskCell(BaseCell):
    """
    Cell used for showing ask price and volume.
    """

    def __init__(self, content: Any, data: Any):
        """"""
        super(AskCell, self).__init__(content, data)

        self.setForeground(COLOR_BLACK)
        self.setForeground(COLOR_ASK)


class PnlCell(BaseCell):
    """
    Cell used for showing pnl data.
    """

    def __init__(self, content: Any, data: Any):
        """"""
        super(PnlCell, self).__init__(content, data)

    def set_content(self, content: Any, data: Any):
        """
        Cell color is set based on whether pnl is 
        positive or negative.
        """
        super(PnlCell, self).set_content(content, data)

        if str(content).startswith("-"):
            self.setForeground(COLOR_SHORT)
        else:
            self.setForeground(COLOR_LONG)


class TimeCell(BaseCell):
    """
    Cell used for showing time string from datetime object.
    """

    def __init__(self, content: Any, data: Any):
        """"""
        super(TimeCell, self).__init__(content, data)

    def set_content(self, content: Any, data: Any):
        """
        Time format is 12:12:12.5
        """
        timestamp = content.strftime("%H:%M:%S")

        millisecond = int(content.microsecond / 1000)
        if millisecond:
            timestamp = f"{timestamp}.{millisecond}"

        self.setText(timestamp)
        self._data = data


class MsgCell(BaseCell):
    """
    Cell used for showing msg data.
    """

    def __init__(self, content: str, data: Any):
        """"""
        super(MsgCell, self).__init__(content, data)
        self.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)


class BaseMonitor(QtWidgets.QTableWidget):
    """
    Monitor data update in VN Trader.
    """

    event_type = ""
    data_key = ""
    sorting = False
    headers = {}

    delete=False

    signal = QtCore.pyqtSignal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super(BaseMonitor, self).__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        self.cells = {}


        self.init_ui()
        self.register_event()

        self.deleted_key=[]

    def init_ui(self):
        """"""
        self.init_table()
        self.init_menu()

    def init_table(self):
        """
        Initialize table.
        """
        self.setColumnCount(len(self.headers))

        labels = [d["display"] for d in self.headers.values()]
        self.setHorizontalHeaderLabels(labels)

        self.verticalHeader().setVisible(False)
        self.setEditTriggers(self.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(self.sorting)

    def init_menu(self):
        """
        Create right click menu.
        """
        self.menu = QtWidgets.QMenu(self)

        resize_action = QtWidgets.QAction("调整列宽", self)
        resize_action.triggered.connect(self.resize_columns)
        self.menu.addAction(resize_action)

        save_action = QtWidgets.QAction("保存数据", self)
        save_action.triggered.connect(self.save_csv)
        self.menu.addAction(save_action)

    def register_event(self):
        """
        Register event handler into event engine.
        """
        if self.event_type:
            self.signal.connect(self.process_event)
            self.event_engine.register(self.event_type, self.signal.emit)

    def process_event(self, event):
        """
        Process new data from event and update into table.
        """
        # Disable sorting to prevent unwanted error.
        if self.sorting:
            self.setSortingEnabled(False)

        # Update data into table.
        data = event.data
        if not self.data_key:
            self.insert_new_row(data)
        else:
            key = data.__getattribute__(self.data_key)

            if key not in self.deleted_key:
                if key in self.cells:
                    self.update_old_row(data)
                else:
                    self.insert_new_row(data)

        # Enable sorting
        if self.sorting:
            self.setSortingEnabled(True)


    def insert_new_row(self, data):
        """
        Insert a new row at the top of table.
        """
        self.insertRow(0)

        row_cells = {}
        for column, header in enumerate(self.headers.keys()):
            setting = self.headers[header]

            content = data.__getattribute__(header)
            cell = setting["cell"](content, data)

            self.setItem(0, column, cell)

            if setting["update"]:
                row_cells[header] = cell

        if self.data_key:
            key = data.__getattribute__(self.data_key)
            self.cells[key] = row_cells

    def update_old_row(self, data):
        """
        Update an old row in table.
        """
        key = data.__getattribute__(self.data_key)
        row_cells = self.cells[key]
        # print(row_cells)
        for header, cell in row_cells.items():
            content = data.__getattribute__(header)
            try:
                cell.set_content(content, data)
            except Exception as e:
                print('异常:',e)



    def resize_columns(self):
        """
        Resize all columns according to contents.
        """
        self.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)

    def save_csv(self):
        """
        Save table data into a csv file
        """
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存数据", "", "CSV(*.csv)")

        if not path:
            return

        with open(path, "w") as f:
            writer = csv.writer(f, lineterminator="\n")

            writer.writerow(self.headers.keys())

            for row in range(self.rowCount()):
                row_data = []
                for column in range(self.columnCount()):
                    item = self.item(row, column)
                    if item:
                        row_data.append(str(item.text()))
                    else:
                        row_data.append("")
                writer.writerow(row_data)

    def contextMenuEvent(self, event):
        """
        Show menu with right click.
        """
        self.menu.popup(QtGui.QCursor.pos())


class TickMonitor(BaseMonitor):
    """
    Monitor for tick data.
    """

    event_type = EVENT_TICK
    sorting = True
    delete=False

    headers = {
        "symbol": {"display": "code", "cell": BaseCell, "update": False},
        "exchange": {"display": "exchange", "cell": EnumCell, "update": False},
        "name": {"display": "name", "cell": BaseCell, "update": True},
        "last_price": {"display": "last_price", "cell": BaseCell, "update": True},
        "last_volume": {"display": "volume", "cell": BaseCell, "update": True},
        "open_price": {"display": "open", "cell": BaseCell, "update": True},
        "high_price": {"display": "high", "cell": BaseCell, "update": True},
        "low_price": {"display": "low", "cell": BaseCell, "update": True},
        "bid_price_1": {"display": "bid price", "cell": BidCell, "update": True},
        "bid_volume_1": {"display": "bid volume", "cell": BidCell, "update": True},
        "ask_price_1": {"display": "ask price", "cell": AskCell, "update": True},
        "ask_volume_1": {"display": "ask volume", "cell": AskCell, "update": True},
        "datetime": {"display": "time", "cell": TimeCell, "update": True},

    }



class TradeMonitor(BaseMonitor):
    """
    Monitor for trade data.
    """

    event_type = EVENT_TRADE
    data_key = "tradeid"
    sorting = True

    delete=True

    headers = {
        "orderid": {"display": "Order id", "cell": BaseCell, "update": False},
        "symbol": {"display": "Code", "cell": BaseCell, "update": False},
        "exchange": {"display": "Exchange", "cell": EnumCell, "update": False},
        "direction": {"display": "Direction", "cell": DirectionCell, "update": False},
        "price": {"display": "Price", "cell": BaseCell, "update": False},
        "volume": {"display": "Volume", "cell": BaseCell, "update": False},
        "time": {"display": "time", "cell": BaseCell, "update": False},

    }


class PositionMonitor(BaseMonitor):
    """
    Monitor for position data.
    """

    event_type = EVENT_POSITION
    data_key = "vt_positionid"
    sorting = True

    delete = False

    headers = {
        "symbol": {"display": "Code", "cell": BaseCell, "update": False},
        "exchange": {"display": "Exchange", "cell": EnumCell, "update": False},
        "direction": {"display": "Direction", "cell": DirectionCell, "update": False},
        "all_volume": {"display": "Position", "cell": BaseCell, "update": True},

        "price": {"display": "Cost", "cell": BaseCell, "update": False},
        "pnl": {"display": "PNL", "cell": PnlCell, "update": True},
    }



class ConnectDialog(QtWidgets.QDialog):
    """
    Start connection of a certain gateway.
    """

    def __init__(self, main_engine: MainEngine, gateway_name: str):
        """"""
        super(ConnectDialog, self).__init__()

        self.main_engine = main_engine
        self.gateway_name = gateway_name
        self.filename = f"connect_{gateway_name.lower()}.json"

        self.widgets = {}

        self.init_ui()

    def init_ui(self):
        """"""
        self.setWindowTitle("Connect")

        # Default setting provides field name, field data type and field default value.
        default_setting = self.main_engine.get_default_setting(
            self.gateway_name)

        # Saved setting provides field data used last time.

        # Initialize line edits and form layout based on setting.
        form = QtWidgets.QFormLayout()

        for field_name, field_value in default_setting.items():
            field_type = type(field_value)

            if field_type == list:
                widget = QtWidgets.QComboBox()
                widget.addItems(field_value)

            else:
                widget = QtWidgets.QLineEdit(str(field_value))


            form.addRow(f"{field_name} <{field_type.__name__}>", widget)
            self.widgets[field_name] = (widget, field_type)

        button = QtWidgets.QPushButton("连接")
        button.clicked.connect(self.connect)
        form.addRow(button)

        self.setLayout(form)

    def connect(self):
        """
        Get setting value from line edits and connect the gateway.
        """
        setting = {}
        for field_name, tp in self.widgets.items():
            widget, field_type = tp
            if field_type == list:
                field_value = str(widget.currentText())
            else:
                field_value = field_type(widget.text())
            setting[field_name] = field_value

        self.main_engine.connect(setting, self.gateway_name)

        self.accept()


class TradingWidget(QtWidgets.QWidget):
    """
    General manual trading widget.
    """

    signal_tick = QtCore.pyqtSignal(Event)

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super(TradingWidget, self).__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine

        self.vt_symbol = ""

        self.init_ui()
        self.register_event()

    def init_ui(self):
        """"""
        self.setFixedWidth(300)

        # Trading function area
        # exchanges = self.main_engine.get_all_exchanges()
        # self.exchange_combo = QtWidgets.QComboBox()
        # self.exchange_combo.addItems([exchange.value for exchange in exchanges])

        self.symbol_line = QtWidgets.QLineEdit()
        self.symbol_line.returnPressed.connect(self.set_vt_symbol)

        self.name_line = QtWidgets.QLineEdit()
        self.name_line.setReadOnly(True)

        self.exchange_line= QtWidgets.QLineEdit()
        self.name_line.setReadOnly(True)

        self.direction_combo = QtWidgets.QComboBox()
        self.direction_combo.addItems(
            [Direction.LONG.value, Direction.SHORT.value])


        self.order_type_combo = QtWidgets.QComboBox()
        self.order_type_combo.addItems(
            [order_type.value for order_type in OrderType])

        double_validator = QtGui.QDoubleValidator()
        double_validator.setBottom(0)

        self.price_line = QtWidgets.QLineEdit()
        self.price_line.setValidator(double_validator)

        self.volume_line = QtWidgets.QLineEdit()
        self.volume_line.setValidator(double_validator)


        send_button = QtWidgets.QPushButton("send order")
        send_button.clicked.connect(self.send_order)


        self.form1 = QtWidgets.QFormLayout()
        self.form1.addRow("Code", self.symbol_line)
        self.form1.addRow("Exchange", self.exchange_line)
        self.form1.addRow("Direction", self.direction_combo)
        self.form1.addRow("Order type", self.order_type_combo)
        self.form1.addRow("price", self.price_line)
        self.form1.addRow("volume", self.volume_line)
        self.form1.addRow(send_button)

        bid_color = "rgb(255,174,201)"
        ask_color = "rgb(160,255,160)"

        self.bp1_label = self.create_label(bid_color)
        self.bp2_label = self.create_label(bid_color)
        self.bp3_label = self.create_label(bid_color)
        self.bp4_label = self.create_label(bid_color)
        self.bp5_label = self.create_label(bid_color)

        self.bv1_label = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)
        self.bv2_label = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)
        self.bv3_label = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)
        self.bv4_label = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)
        self.bv5_label = self.create_label(
            bid_color, alignment=QtCore.Qt.AlignRight)

        self.ap1_label = self.create_label(ask_color)
        self.ap2_label = self.create_label(ask_color)
        self.ap3_label = self.create_label(ask_color)
        self.ap4_label = self.create_label(ask_color)
        self.ap5_label = self.create_label(ask_color)

        self.av1_label = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)
        self.av2_label = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)
        self.av3_label = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)
        self.av4_label = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)
        self.av5_label = self.create_label(
            ask_color, alignment=QtCore.Qt.AlignRight)

        self.lp_label = self.create_label()
        self.return_label = self.create_label(alignment=QtCore.Qt.AlignRight)

        form2 = QtWidgets.QFormLayout()
        form2.addRow(self.ap5_label, self.av5_label)
        form2.addRow(self.ap4_label, self.av4_label)
        form2.addRow(self.ap3_label, self.av3_label)
        form2.addRow(self.ap2_label, self.av2_label)
        form2.addRow(self.ap1_label, self.av1_label)
        form2.addRow(self.lp_label, self.return_label)
        form2.addRow(self.bp1_label, self.bv1_label)
        form2.addRow(self.bp2_label, self.bv2_label)
        form2.addRow(self.bp3_label, self.bv3_label)
        form2.addRow(self.bp4_label, self.bv4_label)
        form2.addRow(self.bp5_label, self.bv5_label)

        # Overall layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(self.form1)
        vbox.addLayout(form2)
        self.setLayout(vbox)

    def create_label(self, color: str = "", alignment: int = QtCore.Qt.AlignLeft):
        """
        Create label with certain font color.
        """
        label = QtWidgets.QLabel()
        if color:
            label.setStyleSheet(f"color:{color}")
        label.setAlignment(alignment)
        return label

    def register_event(self):
        """"""
        self.signal_tick.connect(self.process_tick_event)
        self.event_engine.register(EVENT_TICK, self.signal_tick.emit)

    def process_tick_event(self, event: Event):
        """"""
        tick = event.data


        self.lp_label.setText(str(tick.last_price))
        self.bp1_label.setText(str(tick.bid_price_1))
        self.bv1_label.setText(str(tick.bid_volume_1))
        self.ap1_label.setText(str(tick.ask_price_1))
        self.av1_label.setText(str(tick.ask_volume_1))

        if tick.pre_close:
            r = (tick.last_price / tick.pre_close - 1) * 100
            self.return_label.setText(f"{r:.2f}%")


    def set_vt_symbol(self):
        """
        Set the tick depth data to monitor by vt_symbol.
        """
        symbol = str(self.symbol_line.text())
        if not symbol:
            return


        exchange_value=vt_symbol.split('.')[1]
        self.exchange_line.setText(exchange_value)

        # Generate vt_symbol from symbol and exchange
        # exchange_value = str(self.exchange_combo.currentText())
        vt_symbol = f"{symbol}.{exchange_value}"

        if vt_symbol == self.vt_symbol:
            return
        self.vt_symbol = vt_symbol

        # Update name line widget and clear all labels
        contract = self.main_engine.get_contract(vt_symbol)
        if not contract:
            self.name_line.setText("")
            gateway_name = self.gateway_combo.currentText()
        else:
            self.name_line.setText(contract.name)
            gateway_name = contract.gateway_name

            # Update gateway combo box.
            ix = self.gateway_combo.findText(gateway_name)
            self.gateway_combo.setCurrentIndex(ix)

        self.clear_label_text()

        # Subscribe tick data
        req = SubscribeRequest(
            symbol=symbol, exchange=Exchange(exchange_value)
        )

        self.main_engine.subscribe(req, gateway_name)

        #Update Direction and offset when contract is subscribed
        # if exchange_value=='SSE': r_type_combo)


    def clear_label_text(self):
        """
        Clear text on all labels.
        """
        self.lp_label.setText("")
        self.return_label.setText("")

        self.bv1_label.setText("")
        self.bv2_label.setText("")
        self.bv3_label.setText("")
        self.bv4_label.setText("")
        self.bv5_label.setText("")

        self.av1_label.setText("")
        self.av2_label.setText("")
        self.av3_label.setText("")
        self.av4_label.setText("")
        self.av5_label.setText("")

        self.bp1_label.setText("")
        self.bp2_label.setText("")
        self.bp3_label.setText("")
        self.bp4_label.setText("")
        self.bp5_label.setText("")

        self.ap1_label.setText("")
        self.ap2_label.setText("")
        self.ap3_label.setText("")
        self.ap4_label.setText("")
        self.ap5_label.setText("")

    def send_order(self):
        """
        Send new order manually.
        """
        symbol = str(self.symbol_line.text())
        if not symbol:
            QtWidgets.QMessageBox.critical(self, "failure", "please input Code")
            return

        volume_text = str(self.volume_line.text())
        if not volume_text:
            QtWidgets.QMessageBox.critical(self,"failure", "please input Volume")
            return
        volume = float(volume_text)

        price_text = str(self.price_line.text())
        if not price_text:
            price = 0
        else:
            price = float(price_text)

        req = OrderRequest(
            symbol=symbol,
            exchange=Exchange(str(self.exchange_line.text())),
            direction=Direction(str(self.direction_combo.currentText()).split('/')[0]),
            type=OrderType(str(self.order_type_combo.currentText())),
            volume=volume,
            price=price,
        )

        self.main_engine.send_order(req)

    def cancel_all(self):
        """
        Cancel all active orders.
        """
        order_list = self.main_engine.get_all_active_orders()
        for order in order_list:
            req = order.create_cancel_request()
            self.main_engine.cancel_order(req, order.gateway_name)

