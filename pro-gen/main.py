#!/usr/bin/env python3
"""
Pro-Gen: Spring Boot Project Generator
LLM 기반으로 Spring Boot 프로젝트를 자동 생성하는 도구

Streamlit 웹 애플리케이션으로 실행됩니다.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """메인 실행 함수"""
    # 현재 스크립트의 디렉토리 경로
    current_dir = Path(__file__).parent
    
    # Streamlit 앱 실행
    streamlit_app_path = current_dir / "app.py"
    
    if not streamlit_app_path.exists():
        print(f"오류: Streamlit 앱 파일을 찾을 수 없습니다: {streamlit_app_path}")
        sys.exit(1)
    
    print("🚀 Pro-Gen 시작 중...")
    print(f"📁 작업 디렉토리: {current_dir}")
    print(f"🌐 Streamlit 앱: {streamlit_app_path}")
    print()
    
    try:
        # Streamlit 실행
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_app_path),
            "--server.address", "0.0.0.0",
            "--server.port", "8501"
        ]
        
        subprocess.run(cmd, cwd=current_dir)
        
    except KeyboardInterrupt:
        print("\n👋 Pro-Gen을 종료합니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
