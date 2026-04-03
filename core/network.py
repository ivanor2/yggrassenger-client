import json
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtWebSockets import QWebSocket
from config import BASE_URL, WS_URL


class NetworkClient(QObject):
    logged_in = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    users_loaded = pyqtSignal(list)
    history_loaded = pyqtSignal(list)
    message_sent = pyqtSignal(dict)
    ws_message_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.net = QNetworkAccessManager()
        self.ws = QWebSocket()
        self.token = None
        self.user_id = None

        self.ws.textMessageReceived.connect(self._on_ws_message)

    def _build_url(self, path: str) -> QUrl:
        url = f"{BASE_URL}{path}"
        if self.token:
            sep = "&" if "?" in url else "?"
            url += f"{sep}token={self.token}"
        return QUrl(url)

    def _send_request(self, method: str, path: str, body: dict = None, req_type: str = "default"):
        url = self._build_url(path)
        req = QNetworkRequest(url)
        req.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        payload = json.dumps(body).encode() if body else b""

        reply = self.net.post(req, payload) if method == "POST" else self.net.get(req)
        reply.setProperty("req_type", req_type)
        reply.finished.connect(lambda r=reply: self._process_reply(r))

    def _process_reply(self, reply: QNetworkReply):
        req_type = reply.property("req_type")
        http_status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)

        if reply.error() != QNetworkReply.NetworkError.NoError or (http_status and http_status >= 400):
            err = reply.errorString()
            if http_status == 401:
                err = "Неверный логин или пароль"
            elif http_status == 404:
                err = "Пользователь не найден"
            self.error_occurred.emit(f"{req_type}: {err}")
            reply.deleteLater()
            return

        try:
            data = json.loads(reply.readAll().data().decode())
        except Exception as e:
            self.error_occurred.emit(f"JSON ошибка: {e}")
            reply.deleteLater()
            return

        reply.deleteLater()

        if req_type == "login":
            if "access_token" in data:
                self.token = data["access_token"]
                self._send_request("GET", "/users/me", req_type="me")
            else:
                self.login_failed.emit(data.get("detail", "Ошибка входа"))
        elif req_type == "register":
            self.error_occurred.emit("✅ Регистрация успешна! Войдите в аккаунт.")
        elif req_type == "me":
            self.user_id = data.get("id")
            self.logged_in.emit(data)
            self._connect_ws()
            self.load_users()
        elif req_type == "users":
            self.users_loaded.emit(data)
        elif req_type == "history":
            self.history_loaded.emit(data)
        elif req_type == "send_msg":
            self.message_sent.emit(data)

    # --- Публичные методы API ---
    def login(self, username: str, password: str):
        self._send_request("POST", "/auth/login",
                           {"username": username, "password": password, "email": ""}, "login")

    def register(self, username: str, email: str, password: str):
        self._send_request("POST", "/auth/register",
                           {"username": username, "email": email, "password": password}, "register")

    def load_users(self):
        self._send_request("GET", "/users/", req_type="users")

    def load_history(self, receiver_id: int):
        self._send_request("GET", f"/messages/history/{receiver_id}", req_type="history")

    def send_message(self, receiver_id: int, content: str):
        self._send_request("POST", "/messages/",
                           {"content": content, "receiver_id": receiver_id}, "send_msg")

    # --- WebSocket ---
    def _connect_ws(self):
        ws_url = QUrl(f"{WS_URL}/messages/ws?token={self.token}")
        self.ws.open(ws_url)

    def _on_ws_message(self, text: str):
        try:
            data = json.loads(text)
            if data.get("type") == "new_message":
                self.ws_message_received.emit(data.get("message", {}))
        except Exception:
            pass