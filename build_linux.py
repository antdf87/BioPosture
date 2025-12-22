# build_linux.py
# Engineering Build Script for BioPosture v2.0 - Linux Edition

import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

def clean_build_dirs():
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name, ignore_errors=True)
    
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()

def check_dependencies():
    required_packages = {
        'libnotify': 'notify-send',
        'gtk': 'gtk-launch',
    }
    
    missing = []
    for pkg, cmd in required_packages.items():
        if shutil.which(cmd) is None:
            missing.append(pkg)
    
    if missing:
        print(f"\nWARNING: Missing packages: {', '.join(missing)}")

def build_binary():
    print("\n" + "="*60)
    print("STARTING BUILD PROCESS - BioPosture v2.0 (Linux)")
    print("="*60 + "\n")
    
    check_dependencies()
    clean_build_dirs()
    
    pyinstaller_args = [
        'bioposture_interface.py',
        '--name=BioPosture',
        '--onefile',
        '--add-data=BioPosture.png:.',
        
        '--hidden-import=cv2',
        '--hidden-import=mediapipe',
        '--hidden-import=customtkinter',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        '--hidden-import=numpy',
        
        '--clean',
        '--noconfirm',
        
        '--collect-all=mediapipe',
        '--collect-all=customtkinter',
        '--strip',
    ]
    
    if os.path.exists('BioPosture.png'):
        pyinstaller_args.append('--icon=BioPosture.png')
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        sys.exit(1)
    
    binary_path = Path('dist') / 'BioPosture'
    if binary_path.exists():
        os.chmod(binary_path, 0o755)
        size_mb = binary_path.stat().st_size / (1024 * 1024)
        print("\n" + "="*60)
        print(f"BUILD SUCCESSFUL -> {binary_path.absolute()}")
        print(f"Binary Size: {size_mb:.2f} MB")
        print("="*60)
    else:
        print("\nERROR: Build failed.")
        sys.exit(1)

def create_desktop_file():
    desktop_content = """[Desktop Entry]
Name=BioPosture
Comment=Biometric Posture Monitoring
Exec=/usr/local/bin/BioPosture
Icon=/usr/local/share/icons/BioPosture.png
Terminal=false
Type=Application
Categories=Utility;Healthcare;Science;
Keywords=posture;ergonomics;health;
"""
    
    desktop_file = Path('dist') / 'BioPosture.desktop'
    with open(desktop_file, 'w') as f:
        f.write(desktop_content)
    
    os.chmod(desktop_file, 0o644)

if __name__ == "__main__":
    if sys.platform != "linux":
        print("Script designed for Linux environment.")
        sys.exit(1)
    
    build_binary()
    create_desktop_file()