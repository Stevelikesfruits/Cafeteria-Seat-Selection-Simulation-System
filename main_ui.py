import sys
import os

#将此文件所在的文件夹添加到Python的模块导入搜索列表里
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
#从上面添加的路径里导入ui文件夹里的main_window.py文件里的MainWindow主窗口类
from ui.main_window import MainWindow

#程序的安全入口
#只有直接运行这个文件时，才执行里面的代码；如果这个文件被导入，里面代码不执行
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    #app.exec()保持事件循环，sys.exit()保证安全退出
    sys.exit(app.exec())