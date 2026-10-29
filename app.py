"""Launch the modern desktop application. Team 105."""
import sys
try:
    from PySide6.QtWidgets import QApplication
    from studio import Studio, DARK
except ImportError:
    print("Desktop dependencies are missing. Run Start-Game-Day.bat first.")
    print("For local AI, also run Install-Local-AI.bat.")
    sys.exit(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(DARK)
    window = Studio()
    window.show()
    sys.exit(app.exec())
