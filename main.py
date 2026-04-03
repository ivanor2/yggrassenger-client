import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from config import YGG_SERVER_IP
from core.network import NetworkClient
from ui.auth_dialog import AuthDialog
from ui.chat_window import ChatWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")


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
    if "2xx:xxxx" in YGG_SERVER_IP:
        print("⚠️  ВНИМАНИЕ: Замените YGG_SERVER_IP в config.py на реальный IPv6 вашего сервера!")
    main()