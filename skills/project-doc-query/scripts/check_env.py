#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
check_env.py

project-doc-query skill 启动时环境自检：
1. 检查 Python 版本（>= 3.10）
2. 检查 4 个必需依赖（openpyxl / python-docx / pypdf / chardet）
3. 检查 1 个软依赖（langchain-core）：缺时仅警告不报错
4. 缺必需库时自动 pip install（仅当前 Python 解释器，不强制 conda）

退出码：
  0 - 全部就绪（或仅软依赖缺失，警告但通过）
  1 - 缺 Python
  2 - 缺必需库且自动安装失败
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

# 必需依赖：import name -> pip spec
# 库 import 名可能与 pip 包名不同（如 python-docx 的 import 名是 docx）
REQUIRED_LIBS = {
    "openpyxl": "openpyxl>=3.1.0",
    "docx": "python-docx>=1.1.0",
    "pypdf": "pypdf>=4.0.0",
    "chardet": "chardet>=5.0.0",
}

# 软依赖：import name -> pip spec
# 缺失时仅警告，DocumentLoader 自动退化为 _SimpleDoc 替身，不影响功能
SOFT_LIBS = {
    "langchain_core": "langchain-core>=0.3.0",
}

MIN_PY = (3, 10)


def check_python() -> bool:
    """Phase 1: Python 版本检查"""
    v = sys.version_info
    if v.major < MIN_PY[0] or (v.major == MIN_PY[0] and v.minor < MIN_PY[1]):
        print(f"[FAIL] Python {v.major}.{v.minor}.{v.micro} 不支持，需要 {MIN_PY[0]}.{MIN_PY[1]}+")
        return False
    print(f"[OK] Python {v.major}.{v.minor}.{v.micro}")
    return True


def check_libs() -> list:
    """Phase 2: 必需库检查，返回缺失的 import name 列表"""
    missing = []
    for import_name in REQUIRED_LIBS:
        if importlib.util.find_spec(import_name) is None:
            missing.append(import_name)
            print(f"[MISS] {import_name}")
        else:
            print(f"[OK] {import_name}")
    return missing


def check_soft_libs() -> list:
    """Phase 2.5: 软依赖检查（缺仅警告）"""
    missing_soft = []
    for import_name in SOFT_LIBS:
        if importlib.util.find_spec(import_name) is None:
            missing_soft.append(import_name)
            print(f"[WARN] {import_name} (软依赖，缺失将退化为 _SimpleDoc 替身)")
        else:
            print(f"[OK] {import_name}")
    return missing_soft


def install_libs(missing: list) -> bool:
    """Phase 3: 自动安装缺失的必需库"""
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
    print("project-doc-query skill 环境自检")
    print("=" * 60)

    # Phase 1: Python
    if not check_python():
        print("\n请先安装 Python 3.10+:")
        print("  - Windows: https://www.python.org/downloads/")
        print("  - Conda:   conda create -n AIAssistive python=3.12")
        print("  - 加入 PATH 后重新执行本脚本")
        return 1

    # Phase 2: 必需库
    missing = check_libs()
    if missing and not REQUIREMENTS.exists():
        print(f"\n[FAIL] 缺 requirements.txt: {REQUIREMENTS}")
        return 3

    if missing and not install_libs(missing):
        print(f"\n请手动执行以下命令后再试：")
        print(f"  {sys.executable} -m pip install -r \"{REQUIREMENTS}\"")
        return 2

    # 重新验证必需库
    if missing:
        print("\n[INFO] 重新验证...")
        still_missing = check_libs()
        if still_missing:
            print(f"\n[FAIL] 安装后仍有缺失: {still_missing}")
            print(f"请手动执行: {sys.executable} -m pip install -r \"{REQUIREMENTS}\"")
            return 2

    # Phase 2.5: 软依赖（缺仅警告）
    print()
    missing_soft = check_soft_libs()
    if missing_soft:
        print(f"\n[INFO] 软依赖缺失 {len(missing_soft)} 个，不影响功能但建议安装：")
        for name in missing_soft:
            print(f"  {sys.executable} -m pip install {SOFT_LIBS[name]}")

    # 退出码：必需库全 OK 即通过
    total_req = len(REQUIRED_LIBS)
    ok_count = total_req - len(missing) if not missing else total_req
    if missing_soft:
        print(f"\n[OK] 环境就绪（{ok_count}/{total_req} 必需库，{len(SOFT_LIBS) - len(missing_soft)}/{len(SOFT_LIBS)} 软依赖）")
    else:
        print(f"\n[OK] 环境就绪（{ok_count}/{total_req} 必需库，{len(SOFT_LIBS)}/{len(SOFT_LIBS)} 软依赖）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
