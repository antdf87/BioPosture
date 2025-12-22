# config_manager.py
# Engineering Update v2.0
import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, app_name: str = "BioPosture"):
        self.app_name = app_name
        self.config_dir = self._get_config_directory()
        self.config_file = self.config_dir / "config.json"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_config = {
            "calibration": {
                "iris": 0.0,
                "ht": 0.0,
                "st": 0.0,
                "neck": 0.0,
                "is_calibrated": False
            },
            "thresholds": {
                "soglia_angoli": 10.0,
                "soglia_dist_max": 1.35,
                "soglia_dist_min": 0.65,
                "soglia_compressione": 0.85,
                "tempo_allarme": 5.0,
                "cooldown_notifica": 8.0
            },
            "ui": {
                "camera_index": 0,
                "severity": 50.0,
                "theme": "Dark",
                "notifications_enabled": True,
                "start_minimized": False
            },
            "autostart": {
                "enabled": False,
                "minimized": True
            },
            "session": {
                "total_frames": 0,
                "good_frames": 0,
                "last_session_date": ""
            }
        }
    
    def _get_config_directory(self) -> Path:
        system = platform.system()
        
        if system == "Windows":
            base = os.getenv("APPDATA")
            if not base:
                base = Path.home() / "AppData" / "Roaming"
            else:
                base = Path(base)
        elif system == "Darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home() / ".config"
        
        return base / self.app_name
    
    def load(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return self.default_config.copy()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            
            config = self._deep_merge(self.default_config.copy(), loaded)
            return config
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Errore lettura config: {e}. Uso defaults.")
            return self.default_config.copy()
    
    def save(self, config: Dict[str, Any]) -> bool:
        try:
            if self.config_file.exists():
                backup = self.config_file.with_suffix('.json.bak')
                self.config_file.replace(backup)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            return True
            
        except IOError as e:
            print(f"Errore salvataggio config: {e}")
            return False
    
    def update_section(self, section: str, data: Dict[str, Any]) -> bool:
        config = self.load()
        
        if section not in config:
            return False
        
        config[section].update(data)
        return self.save(config)
    
    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        config = self.load()
        return config.get(section)
    
    def reset_to_defaults(self) -> bool:
        return self.save(self.default_config.copy())
    
    def export_config(self, export_path: str) -> bool:
        try:
            config = self.load()
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Errore export: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            if not isinstance(imported, dict):
                return False
            
            config = self._deep_merge(self.default_config.copy(), imported)
            return self.save(config)
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Errore import: {e}")
            return False
    
    @staticmethod
    def _deep_merge(base: Dict, overlay: Dict) -> Dict:
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get_config_path(self) -> str:
        return str(self.config_file.absolute())

if __name__ == "__main__":
    cm = ConfigManager()
    print(f"Directory configurazione: {cm.config_dir}")
    print(f"File configurazione: {cm.config_file}")
    
    config = cm.load()
    print(json.dumps(config, indent=2))