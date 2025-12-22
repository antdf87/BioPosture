# autostart_manager.py
import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class AutostartManager:
    def __init__(self, app_name: str = "BioPosture", app_path: Optional[str] = None):
        self.app_name = app_name
        self.system = platform.system()
        
        if app_path:
            self.app_path = Path(app_path).absolute()
        else:
            if getattr(sys, 'frozen', False):
                self.app_path = Path(sys.executable).absolute()
            else:
                self.app_path = Path(sys.executable).absolute()
        
        self.registry_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        self.plist_filename = f"com.{app_name.lower()}.plist"
    
    def is_enabled(self) -> bool:
        if self.system == "Windows":
            return self._check_windows_registry()
        elif self.system == "Darwin":
            return self._check_macos_launchagent()
        elif self.system == "Linux":
            return self._check_linux_autostart()
        else:
            return False
    
    def enable(self, minimized: bool = True) -> Tuple[bool, str]:
        if self.system == "Windows":
            return self._enable_windows(minimized)
        elif self.system == "Darwin":
            return self._enable_macos(minimized)
        elif self.system == "Linux":
            return self._enable_linux(minimized)
        else:
            return False, f"Sistema operativo '{self.system}' non supportato"
    
    def disable(self) -> Tuple[bool, str]:
        if self.system == "Windows":
            return self._disable_windows()
        elif self.system == "Darwin":
            return self._disable_macos()
        elif self.system == "Linux":
            return self._disable_linux()
        else:
            return False, f"Sistema operativo '{self.system}' non supportato"
    
    # ---------- WINDOWS ----------
    def _check_windows_registry(self) -> bool:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.registry_key,
                0,
                winreg.KEY_READ
            )
            try:
                winreg.QueryValueEx(key, self.app_name)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    def _enable_windows(self, minimized: bool) -> Tuple[bool, str]:
        try:
            import winreg
            
            cmd = f'"{self.app_path}"'
            if minimized:
                cmd += " --minimized"
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.registry_key,
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, cmd)
            winreg.CloseKey(key)
            
            return True, "Autostart abilitato con successo (registro Windows)"
        
        except Exception as e:
            return False, f"Errore abilitazione autostart Windows: {str(e)}"
    
    def _disable_windows(self) -> Tuple[bool, str]:
        try:
            import winreg
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.registry_key,
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, self.app_name)
                winreg.CloseKey(key)
                return True, "Autostart disabilitato con successo"
            except FileNotFoundError:
                winreg.CloseKey(key)
                return True, "Autostart già disabilitato"
        
        except Exception as e:
            return False, f"Errore disabilitazione autostart Windows: {str(e)}"
    
    # ---------- macOS ----------
    def _check_macos_launchagent(self) -> bool:
        plist_path = Path.home() / "Library" / "LaunchAgents" / self.plist_filename
        return plist_path.exists()
    
    def _enable_macos(self, minimized: bool) -> Tuple[bool, str]:
        try:
            launchagents_dir = Path.home() / "Library" / "LaunchAgents"
            launchagents_dir.mkdir(parents=True, exist_ok=True)
            
            plist_path = launchagents_dir / self.plist_filename
            
            args = [str(self.app_path)]
            if minimized:
                args.append("--minimized")
            
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.{self.app_name.lower()}</string>
    <key>ProgramArguments</key>
    <array>
        {''.join(f'<string>{arg}</string>\n        ' for arg in args)}
        </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>
"""
            
            with open(plist_path, 'w', encoding='utf-8') as f:
                f.write(plist_content)
            
            try:
                subprocess.run(
                    ["launchctl", "load", str(plist_path)],
                    check=False,
                    capture_output=True
                )
            except Exception:
                pass
            
            return True, f"Autostart abilitato (LaunchAgent: {plist_path.name})"
        
        except Exception as e:
            return False, f"Errore abilitazione autostart macOS: {str(e)}"
    
    def _disable_macos(self) -> Tuple[bool, str]:
        try:
            plist_path = Path.home() / "Library" / "LaunchAgents" / self.plist_filename
            
            if not plist_path.exists():
                return True, "Autostart già disabilitato"
            
            try:
                subprocess.run(
                    ["launchctl", "unload", str(plist_path)],
                    check=False,
                    capture_output=True
                )
            except Exception:
                pass
            
            plist_path.unlink()
            
            return True, "Autostart disabilitato con successo"
        
        except Exception as e:
            return False, f"Errore disabilitazione autostart macOS: {str(e)}"
    
    # ---------- LINUX ----------
    def _check_linux_autostart(self) -> bool:
        autostart_path = Path.home() / ".config" / "autostart" / f"{self.app_name}.desktop"
        return autostart_path.exists()
    
    def _enable_linux(self, minimized: bool) -> Tuple[bool, str]:
        try:
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_path = autostart_dir / f"{self.app_name}.desktop"
            
            exec_cmd = str(self.app_path)
            if minimized:
                exec_cmd += " --minimized"
            
            desktop_content = f"""[Desktop Entry]
Type=Application
Name={self.app_name}
Exec={exec_cmd}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Monitoraggio postura biometrico
"""
            
            with open(desktop_path, 'w', encoding='utf-8') as f:
                f.write(desktop_content)
            
            desktop_path.chmod(0o755)
            
            return True, f"Autostart abilitato (desktop file: {desktop_path.name})"
        
        except Exception as e:
            return False, f"Errore abilitazione autostart Linux: {str(e)}"
    
    def _disable_linux(self) -> Tuple[bool, str]:
        try:
            desktop_path = Path.home() / ".config" / "autostart" / f"{self.app_name}.desktop"
            
            if not desktop_path.exists():
                return True, "Autostart già disabilitato"
            
            desktop_path.unlink()
            return True, "Autostart disabilitato con successo"
        
        except Exception as e:
            return False, f"Errore disabilitazione autostart Linux: {str(e)}"
    
    def get_status_info(self) -> dict:
        info = {
            "enabled": self.is_enabled(),
            "system": self.system,
            "app_path": str(self.app_path),
            "config_location": None
        }
        
        if self.system == "Windows":
            info["config_location"] = f"Registry: HKCU\\{self.registry_key}\\{self.app_name}"
        elif self.system == "Darwin":
            info["config_location"] = str(Path.home() / "Library" / "LaunchAgents" / self.plist_filename)
        elif self.system == "Linux":
            info["config_location"] = str(Path.home() / ".config" / "autostart" / f"{self.app_name}.desktop")
        
        return info

if __name__ == "__main__":
    manager = AutostartManager()
    
    print("=== AutostartManager Test ===")
    print(f"Sistema operativo: {manager.system}")
    print(f"Path applicazione: {manager.app_path}")
    print(f"Autostart attualmente abilitato: {manager.is_enabled()}")
    
    info = manager.get_status_info()
    print(f"\nInfo dettagliate:")
    for key, value in info.items():
        print(f"  {key}: {value}")