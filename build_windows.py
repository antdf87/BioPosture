# build_windows.py
# Engineering Build Script for BioPosture v2.0 - Material Edition
# Optimized for Startup Speed

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

def create_version_file():
    version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(2, 0, 0, 0),
    prodvers=(2, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'041004B0',
        [StringStruct(u'CompanyName', u'AntDF87 Engineering'),
        StringStruct(u'FileDescription', u'BioPosture Kinematic Analysis'),
        StringStruct(u'FileVersion', u'2.0.0.0'),
        StringStruct(u'InternalName', u'BioPosture'),
        StringStruct(u'LegalCopyright', u'Copyright 2025 AntDF87'),
        StringStruct(u'OriginalFilename', u'BioPosture.exe'),
        StringStruct(u'ProductName', u'BioPosture System'),
        StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1040, 1200])])
  ]
)
"""
    with open('version_info.txt', 'w') as f:
        f.write(version_info)

def build_exe():
    print("\n" + "="*60)
    print("STARTING BUILD PROCESS - BioPosture v2.0 (Windows)")
    print("="*60 + "\n")
    
    clean_build_dirs()
    create_version_file()
    
    pyinstaller_args = [
        'bioposture_interface.py',              
        '--name=BioPosture',                     
        '--onefile',                             
        '--windowed',                            
        '--icon=BioPosture.ico',                           
        
        # Asset
        '--add-data=BioPosture.ico;.',  
        
        # Optimization
        '--noupx',
        
        # Imports
        '--hidden-import=cv2',
        '--hidden-import=mediapipe',
        '--hidden-import=customtkinter',
        '--hidden-import=pystray',
        '--hidden-import=winotify',
        '--hidden-import=PIL',
        '--hidden-import=numpy',
        
        # Cleanup
        '--clean',                               
        '--noconfirm',                          
        '--version-file=version_info.txt',
        
        # Dependencies
        '--collect-all=mediapipe',              
        '--collect-all=customtkinter',          
    ]
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        sys.exit(1)
    
    exe_path = Path('dist') / 'BioPosture.exe'
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "="*60)
        print(f"BUILD SUCCESSFUL -> {exe_path.absolute()}")
        print(f"Binary Size: {size_mb:.2f} MB")
        print("="*60)
    else:
        print("\nERROR: Build failed.")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform != "win32":
        print("Script designed for Windows environment.")
    build_exe()