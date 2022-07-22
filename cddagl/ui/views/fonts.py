import logging

from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QTabWidget, QGroupBox, QVBoxLayout, QListView, QAbstractItemView, QHBoxLayout

logger = logging.getLogger('cddagl')


class FontsTab(QTabWidget):
    def __init__(self):
        super(FontsTab, self).__init__()

        layout = QGridLayout()

        font_window = CataWindow(4, 4, QFont('Consolas'), 18, 9, 18, False)
        layout.addWidget(font_window, 1, 0)
        self.font_window = font_window

        self.setLayout(layout)

        top_part = QWidget()
        tp_layout = QHBoxLayout()
        tp_layout.setContentsMargins(0, 0, 0, 0)
        self.tp_layout = tp_layout

        installed_gb = QGroupBox()
        tp_layout.addWidget(installed_gb)
        self.installed_gb = installed_gb

        installed_gb_layout = QVBoxLayout()
        installed_gb.setLayout(installed_gb_layout)
        self.installed_gb_layout = installed_gb_layout

        installed_lv = QListView()
        #installed_lv.clicked.connect(self.installed_clicked)
        installed_lv.setEditTriggers(QAbstractItemView.NoEditTriggers)
        installed_gb_layout.addWidget(installed_lv)
        self.installed_lv = installed_lv

        installed_buttons = QWidget()
        ib_layout = QHBoxLayout()
        installed_buttons.setLayout(ib_layout)
        ib_layout.setContentsMargins(0, 0, 0, 0)
        self.ib_layout = ib_layout
        self.installed_buttons = installed_buttons
        installed_gb_layout.addWidget(installed_buttons)

        top_part.setLayout(tp_layout)
        layout.addWidget(top_part)
        self.top_part = top_part


    def set_text(self):
        pass

    def get_main_window(self):
        return self.parentWidget().parentWidget().parentWidget()

    def get_main_tab(self):
        return self.parentWidget().parentWidget().main_tab


class CataWindow(QWidget):
    def __init__(self, terminalwidth, terminalheight, font, fontsize, fontwidth,
            fontheight, fontblending):
        super(CataWindow, self).__init__()

        self.terminalwidth = terminalwidth
        self.terminalheight = terminalheight

        self.cfont = font
        self.fontsize = fontsize
        self.cfont.setPixelSize(fontsize)
        self.cfont.setStyle(QFont.StyleNormal)
        self.fontwidth = fontwidth
        self.fontheight = fontheight
        self.fontblending = fontblending

        self.text = '@@@\nBBB\n@@@\nCCC'
        self.text = '####\n####\n####\n####\n'

    def sizeHint(self):
        return QSize(self.terminalwidth * self.fontwidth,
            self.terminalheight * self.fontheight)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QColor(0, 0, 0))
        painter.setPen(QColor(99, 99, 99));
        painter.setFont(self.cfont)

        term_x = 0
        term_y = 0
        for char in self.text:
            if char == '\n':
                term_y += 1
                term_x = 0
                continue
            x = self.fontwidth * term_x
            y = self.fontheight * term_y

            rect = QRect(x, y, self.fontwidth, self.fontheight)
            painter.drawText(rect, 0, char)

            term_x += 1

        x = self.fontwidth * term_x
        y = self.fontheight * term_y

        rect = QRect(x, y, self.fontwidth, self.fontheight)

        painter.fillRect(rect, Qt.green)