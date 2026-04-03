from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, \
    QListWidgetItem, QTextBrowser, QTextEdit, QPushButton, QMessageBox, QLabel
from PyQt6.QtCore import Qt
from datetime import datetime
from core.network import NetworkClient


class ChatWindow(QMainWindow):
    def __init__(self, network: NetworkClient, user_data: dict):
        super().__init__()
        self.network = network
        self.me = user_data
        self.selected_contact_id = None
        self.contacts_map = {}  # id -> username

        self.setWindowTitle(f"Мессенджер • {self.me['username']}")
        self.resize(900, 650)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Левая панель: Контакты
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.addWidget(QLabel("Контакты"))
        self.contacts_list = QListWidget()
        self.contacts_list.currentItemChanged.connect(self._on_contact_selected)
        left_layout.addWidget(self.contacts_list)
        main_layout.addWidget(left_panel, 2)

        # Правая панель: Чат
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.chat_area = QTextBrowser()
        self.chat_area.setOpenLinks(False)
        right_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.msg_input = QTextEdit()
        self.msg_input.setMaximumHeight(80)
        self.msg_input.setPlaceholderText("Введите сообщение...")
        input_layout.addWidget(self.msg_input)

        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn)
        right_layout.addLayout(input_layout)

        main_layout.addWidget(right_panel, 5)

        # Подключение сигналов сети
        self.network.users_loaded.connect(self._populate_contacts)
        self.network.history_loaded.connect(self._render_history)
        self.network.message_sent.connect(self._append_message)
        self.network.ws_message_received.connect(self._handle_ws_update)
        self.network.error_occurred.connect(lambda e: QMessageBox.warning(self, "Ошибка", e))

        self.network.load_users()

    def _populate_contacts(self, users):
        self.contacts_list.clear()
        self.contacts_map.clear()
        for u in users:
            if u["id"] != self.me["id"]:
                item = QListWidgetItem(u["username"])
                item.setData(Qt.ItemDataRole.UserRole, u["id"])
                self.contacts_list.addItem(item)
                self.contacts_map[u["id"]] = u["username"]

    def _on_contact_selected(self, current, previous):
        if current:
            self.selected_contact_id = current.data(Qt.ItemDataRole.UserRole)
            self.chat_area.clear()
            self.network.load_history(self.selected_contact_id)

    def _render_history(self, messages):
        self.chat_area.clear()
        for msg in sorted(messages, key=lambda x: x.get("timestamp", "")):
            self._append_message(msg, scroll=False)
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def _append_message(self, msg: dict, scroll: bool = True):
        sender_id = msg.get("sender_id")
        is_mine = sender_id == self.me["id"]
        sender_name = self.me["username"] if is_mine else self.contacts_map.get(sender_id, "Неизвестный")
        ts_str = msg.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            time_str = ts.strftime("%H:%M")
        except Exception:
            time_str = ts_str[:5]

        content = msg.get("content", "").replace("\n", "<br>")
        color = "#2563eb" if is_mine else "#16a34a"
        html = f'<div style="margin-bottom: 6px; line-height: 1.4;">'
        html += f'<span style="color: {color}; font-weight: bold;">[{time_str}] {sender_name}: </span> {content}'
        html += f'</div>'

        self.chat_area.append(html)
        if scroll:
            self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def _send_message(self):
        if not self.selected_contact_id:
            QMessageBox.warning(self, "Внимание", "Выберите собеседника")
            return
        text = self.msg_input.toPlainText().strip()
        if not text:
            return
        self.network.send_message(self.selected_contact_id, text)
        self.msg_input.clear()

    def _handle_ws_update(self, msg: dict):
        if self.selected_contact_id and (
                msg.get("sender_id") == self.selected_contact_id or
                msg.get("receiver_id") == self.selected_contact_id
        ):
            self._append_message(msg)
            self._append_message(msg)