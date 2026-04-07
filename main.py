import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings  # <<< ДОБАВИТЬ ИМПОРТ
from core.network import NetworkClient
from ui.auth_dialog import AuthDialog
from ui.chat_window import ChatWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    app.setOrganizationName("YggDev")
    app.setApplicationName("YggMessenger")

    # ✅ Явно указываем INI-формат. Файл будет создан в домашней директории пользователя.
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)

    network = NetworkClient()
    current_user = {}

    auth = AuthDialog(network)
    network.logged_in.connect(lambda data: current_user.update(data))

    if auth.exec() == AuthDialog.DialogCode.Accepted:
        chat = ChatWindow(network, current_user)
        chat.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()