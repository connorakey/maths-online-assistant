import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
import markdown
import requests

from src.shared.screenshot import (
    capture_screenshot,
    optimize_image_for_openai,
    encode_image_to_base64,
    answers_dir,
)

from config import config

current_image_b64 = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>
<style>
  body {{
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    margin: 10px;
    background: #ffffff !important;
    color: #222222 !important;
  }}
  pre {{
    background: #f0f0f0 !important;
    color: #333333 !important;
    padding: 8px;
    overflow-x: auto;
    border-radius: 4px;
  }}
  code {{
    font-family: Consolas, monospace;
  }}
</style>
</head>
<body>
{content}
</body>
</html>
"""


class MathsTutorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maths Online Tutor")
        self.resize(800, 660)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)
        self.setLayout(layout)

        title = QLabel("Maths Online Tutor Application")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #1e1e1e; background-color: white;"
        )
        layout.addWidget(title)

        desc = QLabel(
            "Automatically capture a snippet of your Maths problem and send it to AI for assistance in solving it."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 14px; color: #444444; background-color: white;")
        layout.addWidget(desc)

        hint = QLabel(
            "If you can't figure out the answer, you can click the button below to reveal it."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "font-size: 12px; font-style: italic; color: #666666; background-color: white;"
        )
        layout.addWidget(hint)

        self.screenshot_btn = QPushButton("Take Screenshot")
        self.screenshot_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            """
        )
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        layout.addWidget(self.screenshot_btn)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #ccc;")
        layout.addWidget(separator)

        sol_label = QLabel("Solution:")
        sol_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1e1e1e; background-color: white;"
        )
        layout.addWidget(sol_label)

        self.solution_view = QWebEngineView()
        self.solution_view.setMinimumHeight(200)
        layout.addWidget(self.solution_view)

        ans_label = QLabel("Answer:")
        ans_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1e1e1e; background-color: white;"
        )
        layout.addWidget(ans_label)

        self.reveal_answer_btn = QPushButton("Reveal Answer")
        self.reveal_answer_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 14px;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            """
        )
        self.reveal_answer_btn.clicked.connect(self.show_answer)
        layout.addWidget(self.reveal_answer_btn)

        self.answer_text_label = QLabel("")
        self.answer_text_label.setWordWrap(True)
        self.answer_text_label.setStyleSheet(
            "font-size: 14px; color: #1e1e1e; background-color: white; margin-top: 8px;"
        )
        self.answer_text_label.hide()
        layout.addWidget(self.answer_text_label)

        # Start with blank solution
        self.update_solution("")

        # The answer text to reveal later
        self.answer_text = "This would really be the answer to your question, but you can click the button above to reveal it."

    def take_screenshot(self):
        global current_image_b64
        # Reset UI to initial state
        self.update_solution("")
        self.answer_text_label.hide()
        self.reveal_answer_btn.setEnabled(True)

        screenshot_file = capture_screenshot()

        screenshot_file = answers_dir / screenshot_file
        optimized_image = optimize_image_for_openai(screenshot_file)
        optimized_image = encode_image_to_base64(optimized_image)
        current_image_b64 = optimized_image

        url = f"http://{config["api"]["ip_address"]}:{config["api"]["port"]}/maths-assistant/api"
        data = {
            "api_key": config["api"]["api_key"],
            "image_b64": optimized_image,
            "request_type": "step_by_step",
        }
        response = requests.post(url, json=data)

        updated_solution = response.json().get("step_by_step_guidance", "")
        if not updated_solution:
            updated_solution = "No step-by-step guidance available. Please try again later. A common reason for this is that your API key is invalid or not set, please check your config file."

        self.screenshot_btn.setText("Take Screenshot")
        self.screenshot_btn.setEnabled(True)

        self.update_solution(updated_solution)

        QMessageBox.information(
            self,
            "Success!",
            "The program has successfully captured the screenshot and sent it to the AI for assistance.",
            QMessageBox.StandardButton.Ok,
        )
        self.screenshot_btn.setText("Take Screenshot")

    def update_solution(self, markdown_text: str):
        html_content = markdown.markdown(
            markdown_text, extensions=["fenced_code", "codehilite"]
        )
        full_html = HTML_TEMPLATE.format(content=html_content)
        self.solution_view.setHtml(full_html)

    def show_answer(self):
        global current_image_b64
        if not current_image_b64:
            self.answer_text_label.setText(f"Answer: {self.answer_text}")
            self.answer_text_label.show()
            self.reveal_answer_btn.setEnabled(False)
        else:
            url = f"http://{config['api']['ip_address']}:{config['api']['port']}/maths-assistant/api"
            data = {
                "api_key": config["api"]["api_key"],
                "image_b64": current_image_b64,
                "request_type": "final_answer",
            }
            response = requests.post(url, json=data)
            final_answer = response.json().get("final_answer", "")
            if not final_answer:
                final_answer = "No final answer available. Please try again later."
            self.answer_text_label.setText(f"Answer: {final_answer}")
            self.answer_text_label.show()


def apply_light_palette(app):
    palette = QPalette()

    palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f6f6f6"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#0078d7"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff0000"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#005a9e"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))

    app.setPalette(palette)


def main():
    app = QApplication(sys.argv)
    apply_light_palette(app)
    window = MathsTutorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
