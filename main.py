import os
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QSettings
import download
from template_ui.interface import GeneralWin, GeneralWidget, open_app


class Arg:
    homework = False
    download = False
    test = False


class SampleWidget(GeneralWidget):
    def set_default(self):
        self.settings = QSettings('settings.ini', QSettings.IniFormat)
        if not os.path.exists('settings.ini'):
            self.settings.setValue('DefaultConfigFile', './user_nan.txt')
            self.settings.setValue('DefaultSemester', '19-20秋季')
        else:
            self.lineEdit_input.setText(os.path.abspath(self.settings.value('DefaultConfigFile')))
            self.lineEdit_semester.setText(self.settings.value('DefaultSemester'))

    def bind_widgets(self):
        self.btnBrowser.clicked.connect(self.actOnOpenFile)
        self.btnHomework.clicked.connect(self.interface_homework)
        self.btnDownload.clicked.connect(self.interface_download)

    def print_to_console(self, *args):
        s = " ".join(map(lambda x: "{}".format(x), args))
        self.top_module.console_add(s)

    def interface_homework(self):
        self.top_module.console_clear()
        # output
        download.f_print = self.print_to_console
        # args
        args = Arg()
        args.semester = self.lineEdit_semester.text()
        args.i = self.lineEdit_input.text()
        args.homework = True
        # setting
        self.settings.setValue('DefaultSemester', args.semester)
        self.settings.setValue('DefaultConfigFile', args.i)
        # run
        try:
            download.main(args)
        except Exception:
            print("执行错误！")

    def interface_download(self):
        self.top_module.console_clear()
        # output
        download.f_print = self.print_to_console
        # args
        args = Arg()
        args.semester = self.lineEdit_semester.text()
        args.i = self.lineEdit_input.text()
        args.download = True
        # setting
        self.settings.setValue('DefaultSemester', args.semester)
        self.settings.setValue('DefaultConfigFile', args.i)
        # run
        try:
            download.main(args)
        except Exception:
            print("执行错误！")

    def actOnOpenFile(self):
        folderName, ftype = QFileDialog.getOpenFileName(
            self, '选择输入文件名', self.settings.value('DefaultConfigFile'), "Image Files (*.txt);;All Files (*)")
        print(folderName)
        if folderName == '':
            return
        self.settings.setValue('DefaultConfigFile', folderName)
        print('input', folderName)
        self.lineEdit_input.setText(folderName)


class SampleWindow(GeneralWin):
    def __init__(self, **kwargs):
        super(SampleWindow, self).__init__(**kwargs)

    def get_zoom_ratio(self):
        sw, sh = self.screen_size()
        zoom_ratio = 1 if sw * sh <= 1920 * 1080 \
            else 1 if sw * sh <= 2560 * 1440 \
            else 2  # for high resolution
        return zoom_ratio


if __name__ == "__main__":
    open_app(SampleWindow, OpWidget=SampleWidget)
