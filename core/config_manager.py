import json
from pathlib import Path
from typing import Dict, Optional

class ConfigManager:
    def __init__(self):
        self.config_path = Path('data/config.json')
        self.aliquotas_path = Path('data/aliquotas.json')
        self.empresas_dir = Path('data/empresas')
        self._ensure_directories()
        
    def _ensure_directories(self):
        self.empresas_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self._create_default_config()
        if not self.aliquotas_path.exists():
            self._create_default_aliquotas()
    
    def _create_default_config(self):
        default_config = {
            "aliq_interna_default": 20.5,
            "considerar_desconto": True,
            "usar_credito_manual": False
        }
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
    
    def _create_default_aliquotas(self):
        default_aliquotas = {
            "AC": 12, "AL": 12, "AM": 12, "AP": 12, "BA": 12,
            "CE": 12, "DF": 12, "ES": 12, "GO": 12, "MA": 12,
            "MT": 12, "MS": 12, "MG": 7, "PA": 12, "PB": 12,
            "PR": 7, "PE": 20.5, "PI": 12, "RN": 12, "RJ": 7,
            "RO": 12, "RR": 12, "SC": 7, "SP": 7, "SE": 12,
            "TO": 12
        }
        with open(self.aliquotas_path, 'w') as f:
            json.dump(default_aliquotas, f, indent=2)
    
    def get_config(self) -> Dict:
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def save_config(self, config: Dict):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_aliquota_interestadual(self, uf: str) -> Optional[float]:
        with open(self.aliquotas_path, 'r') as f:
            aliquotas = json.load(f)
            return aliquotas.get(uf.upper())
    
    def get_empresa_config(self, cnpj: str) -> Dict:
        empresa_path = self.empresas_dir / f"{cnpj}.json"
        if empresa_path.exists():
            with open(empresa_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_empresa_config(self, cnpj: str, config: Dict):
        empresa_path = self.empresas_dir / f"{cnpj}.json"
        with open(empresa_path, 'w') as f:
            json.dump(config, f, indent=2)