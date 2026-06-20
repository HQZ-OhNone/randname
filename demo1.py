from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from pathlib import Path

app = QApplication([])
loader = QUiLoader()

ui_file = Path(__file__).parent / "demo.ui"
window = loader.load(str(ui_file))   # 傳字串路徑，而不是 open()
window.show()
app.exec()
