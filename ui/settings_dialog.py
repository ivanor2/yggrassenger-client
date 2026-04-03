from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout
from PyQt6.QtCore import QSettings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки сервера")
        self.resize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~self.windowFlags().WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # Форма настроек
        form_layout = QFormLayout()

        self.server_ip_le = QLineEdit(placeholderText="2001:db8::1")
        self.server_port_le = QLineEdit(placeholderText="8000")
        self.server_port_le.setFixedWidth(100)

        form_layout.addRow("Адрес сервера (IPv6):", self.server_ip_le)
        form_layout.addRow("Порт:", self.server_port_le)

        layout.addLayout(form_layout)

        # Описание
        desc_label = QLabel("Укажите адрес сервера в формате IPv6.\nПример: 2001:db8::1")
        desc_label.setStyleSheet("color: #6b7280; font-size: 12px; margin-top: 8px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Загрузка сохраненных настроек
        self._load_settings()

        # Подключение кнопок
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _load_settings(self):
        settings = QSettings("YggMessenger", "Settings")
        server_ip = settings.value("server_ip", "")
        server_port = settings.value("server_port", "8000")
        
        if server_ip:
            self.server_ip_le.setText(server_ip)
        if server_port:
            self.server_port_le.setText(str(server_port))

    def get_settings(self):
        return {
            "server_ip": self.server_ip_le.text().strip(),
            "server_port": self.server_port_le.text().strip()
        }
