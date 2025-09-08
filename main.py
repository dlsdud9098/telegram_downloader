#!/usr/bin/env python3
"""
Telegram Downloader Automation
자동으로 다운로드 버튼을 감지하고 클릭하며 스크롤하는 프로그램
"""

import sys
from PySide6.QtWidgets import QApplication
from src.ui import MainWindow


def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    app.setApplicationName("Telegram Downloader Automation")
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()
    
    # 애플리케이션 실행
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
