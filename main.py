import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtCore import Qt
import qrcode
from PIL import Image
from io import BytesIO

class QRCodeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern QR Code Generator & Image Viewer")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f9;
                font-family: Arial;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5c6bc0;
                color: white;
                border-radius: 5px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3949ab;
            }
        """)

        self.image_label = QLabel("Uploaded image will appear here")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px dashed #aaa;")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL here")

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text here")
        self.text_input.setFixedHeight(80)

        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.clicked.connect(self.upload_image)

        self.generate_qr_btn = QPushButton("Generate QR Codes")
        self.generate_qr_btn.clicked.connect(self.generate_qr_codes)

        self.save_qr_btn = QPushButton("Save QR Codes")
        self.save_qr_btn.clicked.connect(self.save_qr_codes)
        self.save_qr_btn.setEnabled(False)

        self.qr_url_label = QLabel("QR Code for URL will appear here")
        self.qr_url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_url_label.setStyleSheet("border: 1px solid #ccc;")

        self.qr_text_label = QLabel("QR Code for Text will appear here")
        self.qr_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_text_label.setStyleSheet("border: 1px solid #ccc;")

        self.init_ui()

        # Store generated QR images
        self.qr_url_image = None
        self.qr_text_image = None

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Image upload section
        img_layout = QVBoxLayout()
        img_layout.addWidget(QLabel("Upload Image"))
        img_layout.addWidget(self.image_label)
        img_layout.addWidget(self.upload_btn)

        # URL input section
        url_layout = QVBoxLayout()
        url_layout.addWidget(QLabel("Enter URL"))
        url_layout.addWidget(self.url_input)

        # Text input section
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("Enter Text"))
        text_layout.addWidget(self.text_input)

        # QR code display section
        qr_layout = QHBoxLayout()
        qr_layout.addWidget(self.qr_url_label)
        qr_layout.addWidget(self.qr_text_label)

        # Buttons layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.generate_qr_btn)
        btn_layout.addWidget(self.save_qr_btn)

        main_layout.addLayout(img_layout)
        main_layout.addLayout(url_layout)
        main_layout.addLayout(text_layout)
        main_layout.addLayout(qr_layout)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            ))

    def generate_qr_codes(self):
        url_text = self.url_input.text().strip()
        normal_text = self.text_input.toPlainText().strip()

        if not url_text and not normal_text:
            QMessageBox.warning(self, "Input Error", "Please enter a URL or text to generate QR codes.")
            return

        if url_text:
            self.qr_url_image = self.create_qr(url_text)
            self.qr_url_label.setPixmap(self.pil2pixmap(self.qr_url_image).scaled(
                self.qr_url_label.width(), self.qr_url_label.height(), Qt.AspectRatioMode.KeepAspectRatio
            ))
        else:
            self.qr_url_label.clear()
            self.qr_url_label.setText("No URL provided")

        if normal_text:
            self.qr_text_image = self.create_qr(normal_text)
            self.qr_text_label.setPixmap(self.pil2pixmap(self.qr_text_image).scaled(
                self.qr_text_label.width(), self.qr_text_label.height(), Qt.AspectRatioMode.KeepAspectRatio
            ))
        else:
            self.qr_text_label.clear()
            self.qr_text_label.setText("No text provided")

        if self.qr_url_image or self.qr_text_image:
            self.save_qr_btn.setEnabled(True)

    def save_qr_codes(self):
        if not self.qr_url_image and not self.qr_text_image:
            QMessageBox.warning(self, "Save Error", "No QR codes to save.")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save QR Codes")
        if save_dir:
            if self.qr_url_image:
                self.qr_url_image.save(os.path.join(save_dir, "qr_url.png"))
            if self.qr_text_image:
                self.qr_text_image.save(os.path.join(save_dir, "qr_text.png"))
            QMessageBox.information(self, "Saved", f"QR codes saved successfully in {save_dir}")

    def create_qr(self, data: str) -> Image.Image:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img

    def pil2pixmap(self, image: Image.Image) -> QPixmap:
        # Convert PIL Image to QPixmap
        buf = BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        qimg = QImage.fromData(buf.read())
        return QPixmap.fromImage(qimg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRCodeApp()
    window.show()
    sys.exit(app.exec())
