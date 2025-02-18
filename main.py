import sys
import PySide6.QtWidgets as Qw
from image_viewer import MainWindow

# アプリケーションのエントリーポイント
if __name__ == '__main__':
  app = Qw.QApplication(sys.argv)
  main_window = MainWindow()
  main_window.show()
  sys.exit(app.exec())
