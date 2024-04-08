#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================== #
# This file is a part of PYGPT package               #
# Website: https://pygpt.net                         #
# GitHub:  https://github.com/szczyglis-dev/py-gpt   #
# MIT License                                        #
# Created By  : Marcin Szczygliński                  #
# Updated Date: 2024.03.06 02:00:00                  #
# ================================================== #

import datetime

from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QAction, QIcon, QColor, QPixmap
from PySide6.QtWidgets import QMenu

from pygpt_net.ui.widget.lists.base import BaseList
from pygpt_net.utils import trans
import pygpt_net.icons_rc


class ContextList(BaseList):
    def __init__(self, window=None, id=None):
        """
        Presets select menu

        :param window: main window
        :param id: input id
        """
        super(ContextList, self).__init__(window)
        self.window = window
        self.id = id

        self.doubleClicked.connect(self.dblclick)
        self.setItemDelegate(ImportantItemDelegate())

    def click(self, val):
        """
        Click event

        :param val: click event
        """
        self.window.controller.ctx.select_by_idx(val.row())

    def dblclick(self, val):
        """
        Double click event

        :param val: double click event
        """
        self.window.controller.ctx.select_by_idx(val.row())

    def contextMenuEvent(self, event):
        """
        Context menu event

        :param event: context menu event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        id = self.window.core.ctx.get_id_by_idx(idx)
        ctx_id = id
        ctx = self.window.core.ctx.get_meta_by_id(id)
        if ctx is None:
            return

        is_important = ctx.important

        actions = {}
        actions['rename'] = QAction(QIcon(":/icons/edit.svg"), trans('action.rename'), self)
        actions['rename'].triggered.connect(
            lambda: self.action_rename(event)
        )

        if is_important:
            actions['important'] = QAction(QIcon(":/icons/pin.svg"), trans('action.unpin'), self)
            actions['important'].triggered.connect(
                lambda: self.action_unpin(event)
            )
        else:
            actions['important'] = QAction(QIcon(":/icons/pin.svg"), trans('action.pin'), self)
            actions['important'].triggered.connect(
                lambda: self.action_pin(event)
            )

        actions['duplicate'] = QAction(QIcon(":/icons/copy.svg"), trans('action.duplicate'), self)
        actions['duplicate'].triggered.connect(
            lambda: self.action_duplicate(event)
        )

        actions['delete'] = QAction(QIcon(":/icons/delete.svg"), trans('action.delete'), self)
        actions['delete'].triggered.connect(
            lambda: self.action_delete(event)
        )

        actions['copy_id'] = QAction(QIcon(":/icons/copy.svg"), trans('action.ctx_copy_id') + " @" + str(id), self)
        actions['copy_id'].triggered.connect(
            lambda: self.action_copy_id(event)
        )

        menu = QMenu(self)
        menu.addAction(actions['rename'])
        menu.addAction(actions['duplicate'])
        menu.addAction(actions['important'])
        menu.addAction(actions['delete'])

        # set label menu
        colors = self.window.controller.ui.get_colors()
        set_label_menu = menu.addMenu(trans('calendar.day.label'))
        for status_id, status_info in colors.items():
            name = trans('calendar.day.' + status_info['label'])
            if status_id == 0:
                name = '-'
            color = status_info['color']
            pixmap = QPixmap(16, 16)
            pixmap.fill(color)
            icon = QIcon(pixmap)
            status_action = QAction(icon, name, self)
            status_action.triggered.connect(
                lambda checked=False, s_id=status_id: self.window.controller.ctx.set_label(idx, s_id)
            )
            set_label_menu.addAction(status_action)

        idx_menu = QMenu(trans('action.idx'), self)

        # indexes list
        idxs = self.window.core.config.get('llama.idx.list')
        store = self.window.core.idx.get_current_store()  # get current idx store provider
        if len(idxs) > 0:
            for index in idxs:
                id = index['id']
                name = index['name'] + " (" + index['id'] + ")"

                # add to index
                action = idx_menu.addAction("IDX: " + name)
                action.setIcon(QIcon(":/icons/search.svg"))
                action.triggered.connect(
                    lambda checked=False,
                           idx=idx,
                           index=id: self.action_idx(idx, index)
                )

                # remove from index
                if ctx.indexed is not None and ctx.indexed > 0:

                    # get list of indexes in which context is indexed
                    if store in ctx.indexes:
                        store_indexes = ctx.indexes[store]
                        for store_index in store_indexes:
                            action = idx_menu.addAction(trans("action.idx.remove") + ": " + store_index)
                            action.setIcon(QIcon(":/icons/delete.svg"))
                            action.triggered.connect(
                                lambda checked=False,
                                       store_index=store_index,
                                       ctx_id=ctx_id: self.action_idx_remove(store_index, ctx_id)  # by context meta id
                            )

            menu.addMenu(idx_menu)

        menu.addAction(actions['copy_id'])

        # show last indexed date if available
        if ctx.indexed is not None and ctx.indexed > 0:
            suffix = ""
            if ctx.updated > ctx.indexed:
                suffix = " *"
            dt = datetime.datetime.fromtimestamp(ctx.indexed).strftime("%Y-%m-%d %H:%M")
            action = QAction(QIcon(":/icons/clock.svg"), trans('action.ctx.indexed') + ": " + dt + suffix, self)
            action.setEnabled(False)  # disable action, only for info
            menu.addAction(action)

        if idx >= 0:
            self.window.controller.ctx.select_by_idx(item.row())
            menu.exec_(event.globalPos())

    def action_idx(self, ctx_idx: int, idx: int):
        """
        Index with llama context action handler

        :param ctx_idx: row idx in context list
        :param idx: index name
        """
        self.window.controller.idx.indexer.index_ctx_meta(ctx_idx, idx)

    def action_idx_remove(self, idx: str, meta_id: int):
        """
        Remove from index action handler

        :param idx: index id
        :param meta_id: meta id
        """
        self.window.controller.idx.indexer.index_ctx_meta_remove(idx, meta_id)

    def action_rename(self, event):
        """
        Rename action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.ctx.rename(idx)

    def action_pin(self, event):
        """
        Pin action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.ctx.set_important(idx, True)

    def action_unpin(self, event):
        """
        Unpin action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.ctx.set_important(idx, False)

    def action_duplicate(self, event):
        """
        Rename duplicate handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.ctx.common.duplicate_by_idx(idx)

    def action_important(self, event):
        """
        Set as important action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.ctx.set_important(idx)

    def action_delete(self, event):
        """
        Delete action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.ctx.delete(idx)

    def action_copy_id(self, event):
        """
        Copy ID tag action handler

        :param event: mouse event
        """
        item = self.indexAt(event.pos())
        idx = item.row()
        if idx >= 0:
            self.window.controller.ctx.common.copy_id(idx)


class ImportantItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    Label color delegate

    :param QtWidgets.QStyledItemDelegate: parent class
    """
    def paint(self, painter, option, index):
        super(ImportantItemDelegate, self).paint(painter, option, index)

        # pin (>= 10)
        if index.data(QtCore.Qt.ItemDataRole.UserRole) > 0:
            label = index.data(QtCore.Qt.ItemDataRole.UserRole)
            painter.save()

            if label >= 10:
                color = self.get_color_for_status(3)
                square_size = 3
                square_margin = 0
                square_rect = QtCore.QRect(
                    option.rect.left() + square_margin,
                    option.rect.top() + 2,
                    square_size,
                    square_size,
                )
                painter.setBrush(color)
                painter.setPen(
                    QtGui.QPen(
                        QtCore.Qt.black,
                        0.5,
                        QtCore.Qt.SolidLine,
                    )
                )
                painter.drawRect(square_rect)

                label = label - 10  # remove pin status

            # label (0-9)
            if label > 0:
                color = self.get_color_for_status(label)
                square_size = 5
                square_margin = 0
                square_rect = QtCore.QRect(
                    option.rect.left() + square_margin,
                    option.rect.center().y() - (square_size / 2) + 2,
                    square_size,
                    square_size,
                )
                painter.setBrush(color)
                painter.setPen(QtCore.Qt.NoPen)
                painter.drawRect(square_rect)

            painter.restore()

    def get_color_for_status(self, status: int) -> QColor:
        """
        Get color for status

        :param status: status id
        :return: color
        """
        statuses = {
            0: {'label': 'label.color.default', 'color': QColor(100, 100, 100)},
            1: {'label': 'label.color.red', 'color': QColor(255, 0, 0)},
            2: {'label': 'label.color.orange', 'color': QColor(255, 165, 0)},
            3: {'label': 'label.color.yellow', 'color': QColor(255, 255, 0)},
            4: {'label': 'label.color.green', 'color': QColor(0, 255, 0)},
            5: {'label': 'label.color.blue', 'color': QColor(0, 0, 255)},
            6: {'label': 'label.color.indigo', 'color': QColor(75, 0, 130)},
            7: {'label': 'label.color.violet', 'color': QColor(238, 130, 238)},
        }
        if status in statuses:
            return statuses[status]['color']
        else:
            return statuses[0]['color']
