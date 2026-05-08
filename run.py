"""Proje kök dizininden çalıştır: python run.py"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(__file__))
subprocess.run([sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"])
