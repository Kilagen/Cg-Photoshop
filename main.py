import sys
import traceback

from PyQt6.QtWidgets import QApplication

from back import Backend
from front import PhotoshopWindow


app = QApplication(sys.argv)
backend = Backend()
window = PhotoshopWindow(backend)


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(tb, file=sys.stderr)
    window.error_box.setText(str(exc_value))
    window.error_box.exec()


if __name__ == "__main__":
    sys.excepthook = excepthook
    window.show()
    print(app.exec())
