# build_macos.py
# Engineering Build Script for BioPosture v2.0 - macOS Edition

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

def create_icns_from_png():
    if not os.path.exists('BioPosture.png'):
        return False
    
    try:
        iconset_dir = 'BioPosture.iconset'
        os.makedirs(iconset_dir, exist_ok=True)
        
        sizes = [16, 32, 64, 128, 256, 512]
        
        for size in sizes:
            os.system(f'sips -z {size} {size} BioPosture.png --out {iconset_dir}/icon_{size}x{size}.png')
            os.system(f'sips -z {size*2} {size*2} BioPosture.png --out {iconset_dir}/icon_{size}x{size}@2x.png')
        
        os.system(f'iconutil -c icns {iconset_dir} -o BioPosture.icns')
        shutil.rmtree(iconset_dir)
        return True
    
    except Exception as e:
        print(f"Icon generation error: {e}")
        return False

def build_app():
    print("\n" + "="*60)
    print("STARTING BUILD PROCESS - BioPosture v2.0 (macOS)")
    print("="*60 + "\n")
    
    clean_build_dirs()
    has_icon = create_icns_from_png()
    
    pyinstaller_args = [
        'bioposture_interface.py',
        '--name=BioPosture',
        '--onefile',
        '--windowed',
        '--add-data=BioPosture.png:.',
    ]
    
    if has_icon and os.path.exists('BioPosture.icns'):
        pyinstaller_args.append('--icon=BioPosture.icns')
    
    pyinstaller_args.extend([
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
        '--osx-bundle-identifier=com.antdf87.bioposture',
    ])
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        sys.exit(1)
    
    app_path = Path('dist') / 'BioPosture.app'
    if app_path.exists():
        size_mb = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file()) / (1024 * 1024)
        print("\n" + "="*60)
        print(f"BUILD SUCCESSFUL -> {app_path.absolute()}")
        print(f"Bundle Size: {size_mb:.2f} MB")
        print("="*60)
    else:
        print("\nERROR: Build failed.")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform != "darwin":
        print("Script designed for macOS environment.")
        sys.exit(1)
    build_app()