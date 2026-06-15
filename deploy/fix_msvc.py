"""Post-build: replace frozen PySide6 with full pip source + consolidate DLLs"""
import os
import shutil
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_BASE = r"D:\anaconda_24.10.1\envs_dirs\project_26_3_28"
SRC_PYSIDE6 = os.path.join(PYTHON_BASE, "Lib", "site-packages", "PySide6")
SRC_SHIBOKEN = os.path.join(PYTHON_BASE, "Lib", "site-packages", "shiboken6")
DIST_SRC = os.path.join(PROJECT, "dist")
DIST_DST = os.path.join(PROJECT, "deploy", "dist")
BUILD_DIR = os.path.join(PROJECT, "build")

# Find the _internal directory
internal_dir = None
for root, dirs, files in os.walk(DIST_SRC):
    if os.path.basename(root) == "_internal":
        internal_dir = root
        break

if not internal_dir:
    print("ERROR: _internal directory not found!")
    sys.exit(1)

print(f"_internal: {internal_dir}")

frozen_py6 = os.path.join(internal_dir, "PySide6")

# Step 1: Replace frozen PySide6 with COMPLETE pip PySide6 source
print("Replacing PySide6 with full pip package...")
if os.path.exists(frozen_py6):
    shutil.rmtree(frozen_py6)
shutil.copytree(SRC_PYSIDE6, frozen_py6)

# Step 2: Copy shiboken6.abi3.dll into PySide6
for f in os.listdir(SRC_SHIBOKEN):
    if f.endswith(".dll"):
        shutil.copy2(os.path.join(SRC_SHIBOKEN, f), frozen_py6)
        print(f"  + {f}")

# Step 3: Move root DLLs into PySide6, EXCEPT python3*.dll
# python39.dll MUST stay in root (PyInstaller bootloader looks for it there)
print("Consolidating non-Python DLLs into PySide6/...")
for f in os.listdir(internal_dir):
    if f.endswith(".dll") and not f.lower().startswith("python3"):
        src = os.path.join(internal_dir, f)
        dst = os.path.join(frozen_py6, f)
        if os.path.exists(dst):
            os.remove(src)
            print(f"  rm root: {f}")
        else:
            shutil.move(src, dst)
            print(f"  mv -> PySide6: {f}")

# Step 4: Copy to deploy/dist
if os.path.exists(DIST_DST):
    shutil.rmtree(DIST_DST)
shutil.copytree(DIST_SRC, DIST_DST)
print("Copied to deploy/dist")

# Step 5: Clean build temp
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)

print("Done!")
