import os
import sys

import PyQt5
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget)
from PyQt5 import QtCore


class GeneralWin(QMainWindow):

    def __init__(self, OpWidget=None):
        super().__init__()
        self.cwd = os.path.abspath(os.path.join(__file__, ".."))
        self.uiPath = os.path.join(self.cwd, './ui/GeneralWin.ui')
        PyQt5.uic.loadUi(self.uiPath, self)
        if OpWidget:
            self.set_op_widget(OpWidget)
        self.set_default()
        self.bind_widgets()

    def set_op_widget(self, OpWidget):
        layout = QVBoxLayout()
        self.op_widget = OpWidget()
        layout.addWidget(self.op_widget)
        self.region_op.setLayout(layout)
        self.op_widget.top_module = self

    def screen_size(self):
        screenRect = QApplication.desktop().screenGeometry()
        return [screenRect.width(), screenRect.height()]

    def get_zoom_ratio(self):
        sw, sh = self.screen_size()
        zoom_ratio = 1 if sw * sh <= 1920 * 1080 \
            else 1 if sw * sh <= 2560 * 1440 \
            else 2  # enlarge for high resolution
        return zoom_ratio

    def set_default(self):
        ''' adjust window '''
        self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowCloseButtonHint
                            )
        zoom_ratio = self.get_zoom_ratio()
        self.setFixedSize(int(self.width() * zoom_ratio), int(self.height() * zoom_ratio))  # 固定窗体大小
        self.setWindowTitle('DailyTools')

    def bind_widgets(self):
        ''' binding events '''

    def console_clear(self):
        self.console_set("")

    def console_add(self, textin):
        """ 向终端添加文本 """
        text_add = textin if type(textin) is str else "{}".format(textin)
        text = (self.console.toPlainText() + "\n" + text_add).strip("\n")
        self.console_set(text)

    def console_set(self, textin):
        """ 向终端设置文本 """
        text = textin if type(textin) is str else "{}".format(textin)
        self.console.setPlainText(text)
        scrollbar = self.console.verticalScrollBar()
        if scrollbar:
            scrollbar.setSliderPosition(scrollbar.maximum())


class GeneralWidget(QWidget):
    cwd = ""
    ui_dir_name = "ui"
    ui_file_name = "tools.ui"

    def __init__(self):
        super().__init__()
        PyQt5.uic.loadUi(self.uiPath, self)
        self.set_default()
        self.bind_widgets()

    @property
    def uiPath(self):
        return os.path.join(self.cwd, './%s/%s' % (self.ui_dir_name, self.ui_file_name))

    def set_default(self):
        pass

    def bind_widgets(self):
        ''' binding events '''
        pass


def open_app(Window, **kwargs):
    app = QApplication(sys.argv)
    window = Window(**kwargs)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    open_app(GeneralWin)
