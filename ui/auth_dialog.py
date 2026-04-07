from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
from core.network import NetworkClient
from ui.settings_dialog import SettingsDialog


class AuthDialog(QDialog):
    def __init__(self, network: NetworkClient):
        super().__init__()
        self.network = network
        self.setWindowTitle("Вход в мессенджер")
        self.resize(340, 240)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # Кнопка настроек в верхней части
        settings_btn = QPushButton("⚙ Настройки сервера")
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)

        self.username_le = QLineEdit(placeholderText="Имя пользователя")
        self.email_le = QLineEdit(placeholderText="Email (только для регистрации)")
        self.password_le = QLineEdit(placeholderText="Пароль", echoMode=QLineEdit.EchoMode.Password)

        layout.addWidget(QLabel("Данные аккаунта"))
        layout.addWidget(self.username_le)
        layout.addWidget(self.email_le)
        layout.addWidget(self.password_le)

        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Войти")
        self.reg_btn = QPushButton("Регистрация")
        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.reg_btn)
        layout.addLayout(btn_layout)

        self.status_lbl = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("color: #ef4444; font-size: 12px; margin-top: 8px;")
        layout.addWidget(self.status_lbl)

        self.login_btn.clicked.connect(self._do_login)
        self.reg_btn.clicked.connect(self._do_register)

        self.network.login_failed.connect(self.status_lbl.setText)
        self.network.logged_in.connect(self.accept)
        self.network.error_occurred.connect(self.status_lbl.setText)

    def _open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            print(f"Настройки сохранены")

    def _do_login(self):
        u, p = self.username_le.text().strip(), self.password_le.text().strip()
        if not u or not p:
            self.status_lbl.setText("Заполните логин и пароль")
            return
        self.network.login(u, p)

    def _do_register(self):
        u, e, p = self.username_le.text().strip(), self.email_le.text().strip(), self.password_le.text().strip()
        if not all([u, e, p]):
            self.status_lbl.setText("Заполните все поля")
            return
        self.network.register(u, e, p)