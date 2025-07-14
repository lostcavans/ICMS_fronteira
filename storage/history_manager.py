from typing import List, Dict, Any
from datetime import datetime
from core.models import CalculoICMS
from .database import DatabaseManager

class HistoryManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def save_calculation(self, calculo: CalculoICMS):
        """Salva um cálculo no histórico"""
        self.db.salvar_calculo(calculo)
    
    def get_calculations_by_nfe(self, chNFe: str) -> List[Dict[str, Any]]:
        """Obtém o histórico de cálculos para uma nota fiscal específica"""
        return self.db.obter_calculos_por_nota(chNFe)
    
    def get_all_calculations(self) -> List[Dict[str, Any]]:
        """Obtém todo o histórico de cálculos"""
        return self.db.obter_todos_calculos()
    
    def export_to_csv(self, file_path: str):
        """Exporta o histórico para um arquivo CSV"""
        import csv
        
        calculos = self.get_all_calculations()
        if not calculos:
            return False
        
        fieldnames = [
            'id', 'chNFe', 'data_calculo', 'tipo_calculo', 'considerar_desconto',
            'usar_credito_manual', 'mva_original', 'mva_cnae', 'difal',
            'credito_icms', 'aliquota_reducao', 'aliquota_interna',
            'aliquota_interestadual', 'valor_calculado', 'emitente_CNPJ',
            'dest_CNPJ', 'dest_UF', 'data_emissao'
        ]
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(calculos)
            return True
        except Exception as e:
            print(f"Erro ao exportar para CSV: {str(e)}")
            return False