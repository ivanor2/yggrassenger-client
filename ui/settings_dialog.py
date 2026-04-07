from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox
from PyQt6.QtCore import QSettings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки сервера")
        self.resize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~self.windowFlags().WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.server_ip_le = QLineEdit(placeholderText="2001:db8::1")
        self.server_port_le = QLineEdit(placeholderText="8000")
        self.server_port_le.setFixedWidth(100)

        form_layout.addRow("Адрес сервера (IPv6):", self.server_ip_le)
        form_layout.addRow("Порт:", self.server_port_le)
        layout.addLayout(form_layout)

        desc_label = QLabel("Укажите реальный IPv6-адрес сервера Yggdrasil.")
        desc_label.setStyleSheet("color: #6b7280; font-size: 12px; margin-top: 8px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self._load_settings()
        # Важно: сохраняем ДО закрытия окна
        self.save_btn.clicked.connect(self._save_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def _load_settings(self):
        try:
            settings = QSettings()
            ip = settings.value("server_ip", "", type=str)
            port = settings.value("server_port", "8000", type=str)
            if ip: self.server_ip_le.setText(ip)
            if port: self.server_port_le.setText(str(port))
        except Exception:
            pass

    def _save_and_accept(self):
        ip = self.server_ip_le.text().strip()
        port = self.server_port_le.text().strip()

        if not ip:
            QMessageBox.warning(self, "Ошибка", "Введите IPv6-адрес сервера")
            return

        try:
            settings = QSettings()
            settings.setValue("server_ip", ip)
            settings.setValue("server_port", port)
            settings.sync()  # Принудительная запись на диск

            # ✅ Проверяем, прошла ли запись успешно
            if settings.status() != QSettings.Status.NoError:
                raise PermissionError(
                    "Нет прав на запись файла настроек. Запустите от имени пользователя или проверьте права папки ~/.config/")

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить настройки:\n{str(e)}")