#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
check_env.py

project-doc-write skill 启动时环境自检：
1. 检查 Python 版本（>= 3.10）
2. 检查 4 个必需依赖（openpyxl / python-docx / pypdf / chardet）
3. 缺库时自动 pip install（仅当前 Python 解释器，不强制 conda）

退出码：
  0 - 全部就绪
  1 - 缺 Python
  2 - 缺库且自动安装失败
  3 - 缺 requirements.txt

Usage:
    python scripts/check_env.py
"""

import sys
import subprocess
import importlib.util
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REQUIREMENTS = SCRIPTS_DIR / "requirements.txt"

REQUIRED_LIBS = {
    "openpyxl": "openpyxl>=3.1.0",
    "docx": "python-docx>=1.1.0",
    "pypdf": "pypdf>=4.0.0",
    "chardet": "chardet>=5.0.0",
}

MIN_PY = (3, 10)


def check_python() -> bool:
    v = sys.version_info
    if v.major < MIN_PY[0] or (v.major == MIN_PY[0] and v.minor < MIN_PY[1]):
        print(f"[FAIL] Python {v.major}.{v.minor}.{v.micro} 不支持，需要 {MIN_PY[0]}.{MIN_PY[1]}+")
        return False
    print(f"[OK] Python {v.major}.{v.minor}.{v.micro}")
    return True


def check_libs() -> list:
    missing = []
    for import_name in REQUIRED_LIBS:
        if importlib.util.find_spec(import_name) is None:
            missing.append(import_name)
            print(f"[MISS] {import_name}")
        else:
            print(f"[OK] {import_name}")
    return missing


def install_libs(missing: list) -> bool:
    if not REQUIREMENTS.exists():
        print(f"[FAIL] 未找到 {REQUIREMENTS}")
        return False
    pip_specs = [REQUIRED_LIBS[m] for m in missing if m in REQUIRED_LIBS]
    if not pip_specs:
        return True
    print(f"\n[INFO] 正在自动安装 {len(pip_specs)} 个缺失库: {pip_specs}")
    cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + pip_specs
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"[OK] pip install 完成")
            return True
        print(f"[FAIL] pip install 失败 (returncode={result.returncode})")
        if result.stderr:
            print(result.stderr[:1000])
        return False
    except subprocess.TimeoutExpired:
        print(f"[FAIL] pip install 超时（>300s）")
        return False
    except Exception as e:
        print(f"[FAIL] pip 调用异常: {e}")
        return False


def main() -> int:
    print("=" * 60)
    print("project-doc-write skill 环境自检")
    print("=" * 60)

    if not check_python():
        print("\n请先安装 Python 3.10+:")
        print("  - Windows: https://www.python.org/downloads/")
        print("  - Conda:   conda create -n AIAssistive python=3.12")
        print("  - 加入 PATH 后重新执行本脚本")
        return 1

    missing = check_libs()
    if not missing:
        print(f"\n[OK] 环境就绪（{len(REQUIRED_LIBS)}/{len(REQUIRED_LIBS)} 库）")
        return 0

    if not REQUIREMENTS.exists():
        print(f"\n[FAIL] 缺 requirements.txt: {REQUIREMENTS}")
        return 3

    if not install_libs(missing):
        print(f"\n请手动执行以下命令后再试：")
        print(f"  {sys.executable} -m pip install -r \"{REQUIREMENTS}\"")
        return 2

    print("\n[INFO] 重新验证...")
    still_missing = check_libs()
    if still_missing:
        print(f"\n[FAIL] 安装后仍有缺失: {still_missing}")
        print(f"请手动执行: {sys.executable} -m pip install -r \"{REQUIREMENTS}\"")
        return 2

    print(f"\n[OK] 环境就绪（{len(REQUIRED_LIBS)}/{len(REQUIRED_LIBS)} 库）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
