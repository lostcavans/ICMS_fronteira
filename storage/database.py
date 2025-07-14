import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from core.models import CalculoICMS

class DatabaseManager:
    def __init__(self, db_path: str = "data/icms_fronteira.db"):
        self.db_path = Path(db_path)
        self._initialize_db()
    
    def _initialize_db(self):
        """Cria o banco de dados e as tabelas se não existirem"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de cálculos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calculos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chNFe TEXT NOT NULL,
                    data_calculo TEXT NOT NULL,
                    tipo_calculo TEXT NOT NULL,
                    considerar_desconto INTEGER NOT NULL,
                    usar_credito_manual INTEGER NOT NULL,
                    mva_original REAL NOT NULL,
                    mva_cnae REAL NOT NULL,
                    difal REAL NOT NULL,
                    credito_icms REAL NOT NULL,
                    aliquota_reducao REAL NOT NULL,
                    aliquota_interna REAL NOT NULL,
                    aliquota_interestadual REAL NOT NULL,
                    valor_calculado REAL NOT NULL,
                    formula_utilizada TEXT NOT NULL,
                    FOREIGN KEY (chNFe) REFERENCES notas(chNFe)
                )
            """)
            
            # Tabela de notas fiscais (para referência)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notas (
                    chNFe TEXT PRIMARY KEY,
                    emitente_CNPJ TEXT NOT NULL,
                    emitente_CRT INTEGER NOT NULL,
                    dest_CNPJ TEXT NOT NULL,
                    dest_UF TEXT NOT NULL,
                    data_emissao TEXT NOT NULL,
                    valor_total REAL NOT NULL
                )
            """)
            
            conn.commit()
    
    def salvar_calculo(self, calculo: CalculoICMS):
        """Salva um cálculo no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Primeiro, verifica se a nota já está cadastrada
            cursor.execute("SELECT 1 FROM notas WHERE chNFe = ?", (calculo.chNFe,))
            if not cursor.fetchone():
                # Se não estiver, insere (nota fictícia - em produção, deveria vir do XML)
                cursor.execute("""
                    INSERT INTO notas (chNFe, emitente_CNPJ, emitente_CRT, dest_CNPJ, dest_UF, data_emissao, valor_total)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    calculo.chNFe,
                    "07378783000190",  # CNPJ emitente exemplo
                    3,  # CRT exemplo
                    "13230092000148",  # CNPJ destinatário exemplo
                    "PE",  # UF destinatário exemplo
                    datetime.now().isoformat(),  # Data exemplo
                    8430.06  # Valor total exemplo
                ))
            
            # Insere o cálculo
            cursor.execute("""
                INSERT INTO calculos (
                    chNFe, data_calculo, tipo_calculo, considerar_desconto, usar_credito_manual,
                    mva_original, mva_cnae, difal, credito_icms, aliquota_reducao,
                    aliquota_interna, aliquota_interestadual, valor_calculado, formula_utilizada
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                calculo.chNFe,
                calculo.data_calculo.isoformat(),
                calculo.tipo_calculo,
                int(calculo.considerar_desconto),
                int(calculo.usar_credito_manual),
                calculo.mva_original,
                calculo.mva_cnae,
                calculo.difal,
                calculo.credito_icms,
                calculo.aliquota_reducao,
                calculo.aliquota_interna,
                calculo.aliquota_interestadual,
                calculo.valor_calculado,
                calculo.formula_utilizada
            ))
            
            conn.commit()
    
    def obter_calculos_por_nota(self, chNFe: str) -> List[Dict[str, Any]]:
        """Obtém todos os cálculos realizados para uma nota fiscal"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM calculos 
                WHERE chNFe = ?
                ORDER BY data_calculo DESC
            """, (chNFe,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def obter_todos_calculos(self) -> List[Dict[str, Any]]:
        """Obtém todos os cálculos armazenados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.*, n.emitente_CNPJ, n.dest_CNPJ, n.dest_UF, n.data_emissao
                FROM calculos c
                JOIN notas n ON c.chNFe = n.chNFe
                ORDER BY c.data_calculo DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]