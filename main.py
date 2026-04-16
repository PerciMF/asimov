import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import AIAssistantWindow


def main() -> None:
    app = QApplication(sys.argv)

    window = AIAssistantWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()