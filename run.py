"""
Proje kökünden veya backend/ içinden çalıştırılabilir:
    python run.py          (proje kökünden)
    python ../run.py       (backend/ içinden)
"""
import subprocess
import sys
import os

# Bu dosyanın konumuna göre backend/ klasörünü bul
_this_dir = os.path.dirname(os.path.abspath(__file__))

# run.py proje kökünde → backend/ alt klasörü
# run.py backend/ içindeyse (sembolik link vb.) → mevcut klasör
if os.path.isdir(os.path.join(_this_dir, "backend")):
    backend_dir = os.path.join(_this_dir, "backend")
else:
    backend_dir = _this_dir

os.chdir(backend_dir)
subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload"])
