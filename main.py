
import sys
import smtplib
import re
from email.mime.text import MIMEText

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation


class MDCUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MDC")
        self.setGeometry(100, 100, 1200, 700)

        # -----------------------------
        # Images
        # -----------------------------
        self.image_paths = ["image1.jpg", "image2.jpg" ]
        self.current_index = 0

        self.bg1 = QLabel(self)
        self.bg2 = QLabel(self)

        for bg in (self.bg1, self.bg2):
            bg.setGeometry(0, 0, 2000, 1200)
            bg.setScaledContents(True)

        self.bg1.setPixmap(QPixmap(self.image_paths[0]))

        # Fade effect
        self.opacity = QGraphicsOpacityEffect()
        self.bg2.setGraphicsEffect(self.opacity)
        self.opacity.setOpacity(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.fade_to_next)
        self.timer.start(2000)

        # -----------------------------
        # Dark overlay
        # -----------------------------
        self.overlay = QLabel(self)
        self.overlay.setGeometry(0, 0, 2000, 1200)
        self.overlay.setStyleSheet("background-color: rgba(0,0,0,180);")

        # -----------------------------
        # Layout
        # -----------------------------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(60, 30, 60, 50)

        # Top bar
        top_layout = QHBoxLayout()

        logo = QLabel("MDC")
        logo.setStyleSheet("color: #e50914;")
        logo.setFont(QFont("Arial", 22, QFont.Bold))

        sign_in = QPushButton("Sign In")
        sign_in.setStyleSheet("""
            QPushButton {
                padding: 10px 18px;
                font-size: 13px;
                border: none;
                background-color: #e50914;
                color: white;
            }
            QPushButton:hover {
                background-color: #f6121d;
            }
        """)

        top_layout.addWidget(logo)
        top_layout.addStretch()
        top_layout.addWidget(sign_in)

        # Center content
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Discover Movies You'll Love")
        title.setStyleSheet("color: white;")
        title.setFont(QFont("Arial", 34, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Personalized picks. No endless scrolling.")
        subtitle.setStyleSheet("color: white;")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setAlignment(Qt.AlignCenter)

        desc = QLabel("Enter your email to start exploring your perfect movie list.")
        desc.setStyleSheet("color: white;")
        desc.setFont(QFont("Arial", 12))
        desc.setAlignment(Qt.AlignCenter)

        # -----------------------------
        # FORM
        # -----------------------------
        form_layout = QHBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setSpacing(0)

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email address")
        self.email.setFixedWidth(350)
        self.email.setFixedHeight(45)

        self.email.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                background: rgba(0,0,0,0.6);
                color: white;
                border: 1.5px solid gray;
            }
            QLineEdit:hover {
                border: 1.5px solid orange;
            }
            QLineEdit:focus {
                border: 1.5px solid #e50914;
            }
        """)

        button = QPushButton("Get Started >")
        button.setFixedWidth(180)
        button.setFixedHeight(45)

        button.setStyleSheet("""
            QPushButton {
                background-color: #e50914;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #f6121d;
            }
        """)

        # CONNECT BUTTON
        button.clicked.connect(self.send_email)

        form_layout.addWidget(self.email)
        form_layout.addWidget(button)

        # Add widgets
        center_layout.addWidget(title)
        center_layout.addSpacing(15)
        center_layout.addWidget(subtitle)
        center_layout.addSpacing(10)
        center_layout.addWidget(desc)
        center_layout.addSpacing(25)
        center_layout.addLayout(form_layout)

        main_layout.addLayout(top_layout)
        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    # -----------------------------
    # EMAIL FUNCTION
    # -----------------------------
    def send_email(self):
        user_email = self.email.text().strip()

        if not user_email:
            QMessageBox.warning(self, "Error", "Please enter an email!")
            return

        # ✅ Email validation
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, user_email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address!")
            return

        sender_email = "amaanshaikh9991@gmail.com"
        receiver_email = "amaanshaikh9991@gmail.com"
        app_password = "diykauwnfgrazvkl"  # 🔥 replace this

        subject = "New User Login"
        body = f"{user_email} has logged in"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            server.quit()

            QMessageBox.information(self, "Success", "Email submitted!")
            self.email.clear()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to send email\n{e}")

    # -----------------------------
    # Fade transition
    # -----------------------------
    def fade_to_next(self):
        self.current_index = (self.current_index + 1) % len(self.image_paths)

        self.bg2.setPixmap(QPixmap(self.image_paths[self.current_index]))

        self.anim = QPropertyAnimation(self.opacity, b"opacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.finished.connect(self.swap_images)
        self.anim.start()

    def swap_images(self):
        self.bg1.setPixmap(self.bg2.pixmap())
        self.opacity.setOpacity(0)


# -----------------------------
# RUN
# -----------------------------
app = QApplication(sys.argv)
window = MDCUI()
window.show()
sys.exit(app.exec_())