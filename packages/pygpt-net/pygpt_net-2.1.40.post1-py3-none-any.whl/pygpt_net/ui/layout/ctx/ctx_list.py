#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.02.02 17:00:00                  #
# ================================================== #

from PySide6 import QtCore
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget
from datetime import datetime, timedelta

from pygpt_net.ui.widget.element.labels import TitleLabel
from pygpt_net.ui.widget.lists.context import ContextList
from pygpt_net.utils import trans


class CtxList:
    def __init__(self, window=None):
        """
        Context list UI

        :param window: Window instance
        """
        self.window = window

    def setup(self) -> QWidget:
        """
        Setup list

        :return: QWidget
        """
        id = 'ctx.list'
        self.window.ui.nodes['ctx.new'] = QPushButton(trans('ctx.new'))
        self.window.ui.nodes['ctx.new'].clicked.connect(
            lambda: self.window.controller.ctx.new())

        self.window.ui.nodes[id] = ContextList(self.window, id)
        self.window.ui.nodes[id].selection_locked = self.window.controller.ctx.context_change_locked
        self.window.ui.nodes['ctx.label'] = TitleLabel(trans("ctx.list.label"))

        layout = QVBoxLayout()
        layout.addWidget(self.window.ui.nodes['ctx.new'])
        layout.addWidget(self.window.ui.nodes[id])
        layout.setContentsMargins(0, 0, 0, 0)

        self.window.ui.models[id] = self.create_model(self.window)
        self.window.ui.nodes[id].setModel(self.window.ui.models[id])
        self.window.ui.nodes[id].selectionModel().selectionChanged.connect(
            lambda: self.window.controller.ctx.selection_change())

        widget = QWidget()
        widget.setLayout(layout)
        widget.setContentsMargins(0, 0, 0, 0)

        return widget

    def create_model(self, parent) -> QStandardItemModel:
        """
        Create model

        :param parent: parent widget
        :return: QStandardItemModel
        """
        return QStandardItemModel(0, 1, parent)

    def update(self, id, data):
        """
        Update list

        :param id: ID of the list
        :param data: Data to update
        """
        self.window.ui.nodes[id].backup_selection()
        self.window.ui.models[id].removeRows(0, self.window.ui.models[id].rowCount())
        i = 0
        for n in data:
            self.window.ui.models[id].insertRow(i)
            dt = self.convert_date(data[n].updated)
            date_time_str = datetime.fromtimestamp(data[n].updated).strftime("%Y-%m-%d %H:%M")
            title = data[n].name
            # truncate to max 40 chars
            if len(title) > 80:
                title = title[:80] + '...'
            name = title.replace("\n", "") + ' (' + dt + ')'
            index = self.window.ui.models[id].index(i, 0)
            mode_str = ''
            if data[n].last_mode is not None:
                mode_str = " ({})".format(trans('mode.' + data[n].last_mode))
            tooltip_text = "{}: {}{} #{}".format(
                date_time_str,
                data[n].name,
                mode_str,
                n,
            )
            self.window.ui.models[id].setData(index, tooltip_text, QtCore.Qt.ToolTipRole)
            if data[n].important:
                self.window.ui.models[id].setData(index, data[n].label + 10, QtCore.Qt.ItemDataRole.UserRole)
            else:
                self.window.ui.models[id].setData(index, data[n].label, QtCore.Qt.ItemDataRole.UserRole)
            self.window.ui.models[id].setData(self.window.ui.models[id].index(i, 0), name)
            i += 1

        self.window.ui.nodes[id].restore_selection()

    def convert_date(self, timestamp: int) -> str:
        """
        Convert timestamp to human readable format

        :param timestamp: timestamp
        :return: string
        """
        today = datetime.today().date()
        yesterday = today - timedelta(days=1)
        date = datetime.fromtimestamp(timestamp).date()

        days_ago = (today - date).days
        weeks_ago = days_ago // 7

        if date == today:
            return trans('dt.today')
        elif date == yesterday:
            return trans('dt.yesterday')
        elif weeks_ago == 1:
            return trans('dt.week')
        elif 1 < weeks_ago < 4:
            return f"{weeks_ago} " + trans('dt.weeks')
        elif days_ago < 30:
            return f"{days_ago} " + trans('dt.days_ago')
        elif 30 <= days_ago < 32:
            return trans('dt.month')
        else:
            return date.strftime("%Y-%m-%d")
