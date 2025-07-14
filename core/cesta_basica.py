import json
from pathlib import Path
from typing import Dict, Optional, List

class Produto:
    """Classe modelo para representar um produto da NFe"""
    def __init__(self, item: str = "", descricao: str = "", ncm: str = "", cest: str = "",
                 valor_total: float = 0.0, valor_icms: float = 0.0):
        self.item = item
        self.descricao = descricao
        self.ncm = ncm
        self.cest = cest
        self.valor_total = valor_total
        self.valor_icms = valor_icms

class CestaBasicaCalculator:
    """Classe para cálculo de ICMS para itens da cesta básica conforme legislação atual"""
    
    def __init__(self):
        # Inicializa as alíquotas primeiro
        self.aliquota_padrao = 20.0  # 20%
        self.aliquota_reducao = 0.4   # 40% da alíquota padrão (redução de 60%)
        
        # Carrega as configurações
        self.pautas = self._carregar_pautas()
        self.itens_zero = self._carregar_itens_zero()
        self.itens_reduzidos = self._carregar_itens_reduzidos()
        self.itens_seletivos = self._carregar_itens_seletivos()

    def _carregar_pautas(self) -> Dict[str, float]:
        """Carrega os valores de pauta fiscal do arquivo JSON"""
        try:
            with open(Path('data/pauta_cesta_basica.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _carregar_itens_zero(self) -> Dict[str, Dict]:
        """Define os itens da cesta básica com alíquota zero"""
        return {
            # Açúcar
            '1701': {'desc': 'Açúcar', 'aliq': 0.0},
            # Arroz
            '1006': {'desc': 'Arroz', 'aliq': 0.0},
            # Carnes
            '0201': {'desc': 'Carne bovina', 'aliq': 0.0},
            '0210': {'desc': 'Carne bovina preparada', 'aliq': 0.0},  # Adicionado
            '0202': {'desc': 'Carne suína', 'aliq': 0.0},
            '0204': {'desc': 'Carne ovina/caprina', 'aliq': 0.0},
            '0207': {'desc': 'Carne de aves', 'aliq': 0.0},
            # Leite e derivados
            '0401': {'desc': 'Leite', 'aliq': 0.0},
            '0406': {'desc': 'Queijos', 'aliq': 0.0, 'tipos': [
                'muçarela', 'minas', 'prato', 'coalho', 'ricota', 
                'requeijão', 'provolone', 'parmesão', 'fresco', 'reino'
            ]},
            # Farinhas
            '1101': {'desc': 'Farinha de trigo', 'aliq': 0.0},
            '1102': {'desc': 'Farinha de mandioca/tapioca', 'aliq': 0.0},
            # Feijão
            '0713': {'desc': 'Feijão', 'aliq': self._get_aliquota_feijao},
            # Outros itens
            '0901': {'desc': 'Café', 'aliq': 0.0},
            '1902': {'desc': 'Massas alimentícias', 'aliq': 0.0},
            '1905': {'desc': 'Pão francês', 'aliq': 0.0},
            '0302': {'desc': 'Peixes', 'aliq': 0.0, 'exceto': [
                'salmão', 'bacalhau', 'atum', 'hadoque', 'saithe', 'ovas'
            ]},
            '2501': {'desc': 'Sal', 'aliq': 0.0}
        }

    def _carregar_itens_reduzidos(self) -> Dict[str, Dict]:
        """Define itens com alíquota reduzida (60% da padrão)"""
        return {
            '1103': {'desc': 'Amido de milho', 'aliq': self.aliquota_padrao * self.aliquota_reducao},
            '2002': {'desc': 'Extrato de tomate', 'aliq': self.aliquota_padrao * self.aliquota_reducao},
            '2106': {'desc': 'Leite fermentado', 'aliq': self.aliquota_padrao * self.aliquota_reducao},
            '0403': {'desc': 'Iogurte', 'aliq': self.aliquota_padrao * self.aliquota_reducao},
            '2009': {'desc': 'Sucos naturais', 'aliq': self.aliquota_padrao * self.aliquota_reducao,
                    'condicoes': ['sem açúcar', 'sem edulcorantes', 'sem conservantes']}
        }

    def _carregar_itens_seletivos(self) -> Dict[str, Dict]:
        """Define itens com imposto seletivo (sobretaxa)"""
        return {
            '2203': {'desc': 'Cerveja', 'aliq': 30.0},  # 30%
            '2208': {'desc': 'Bebidas alcoólicas', 'aliq': 30.0},
            '2202': {'desc': 'Refrigerantes', 'aliq': 25.0},  # 25%
            '2402': {'desc': 'Cigarros', 'aliq': 35.0}  # 35%
        }

    def _get_aliquota_feijao(self, uf_origem: str) -> float:
        """Retorna alíquota específica para feijão conforme origem"""
        regioes_5pct = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 
                       'MA', 'MT', 'MS', 'PI', 'RN', 'RO', 'RR', 'SE', 'TO']
        return 5.0 if uf_origem in regioes_5pct else 10.0

    def _get_ncm_base(self, ncm: str) -> str:
        """Normaliza e retorna os 4 primeiros dígitos do NCM"""
        return ncm.zfill(8)[:4]

    def is_cesta_basica(self, produto: Produto) -> bool:
        """Verifica se o produto é da cesta básica com alíquota zero"""
        ncm_base = self._get_ncm_base(produto.ncm)
        
        # Verifica pelo NCM (02102000 -> 0210)
        if ncm_base in ['0201', '0210']:  # Carnes bovinas e preparadas
            return True
            
        # Verifica pelo CEST (1708301)
        if produto.cest and produto.cest.startswith('1708301'):
            return True
            
        return False

    def get_categoria_produto(self, produto: Produto) -> Dict:
        """Identifica a categoria tributária do produto"""
        ncm_base = self._get_ncm_base(produto.ncm)
        desc_lower = produto.descricao.lower()
        
        # 1. Verifica itens seletivos
        for ncm, regras in self.itens_seletivos.items():
            if ncm_base == ncm or any(p in desc_lower for p in regras['desc'].lower().split()):
                return {'tipo': 'seletivo', 'regras': regras}
        
        # 2. Verifica cesta básica (alíquota zero)
        for ncm, regras in self.itens_zero.items():
            if ncm_base == ncm or any(p in desc_lower for p in regras['desc'].lower().split()):
                # Verifica exceções
                if 'exceto' in regras and any(e in desc_lower for e in regras['exceto']):
                    continue
                if 'tipos' in regras and not any(t in desc_lower for t in regras['tipos']):
                    continue
                return {'tipo': 'zero', 'regras': regras}
        
        # 3. Verifica itens com redução
        for ncm, regras in self.itens_reduzidos.items():
            if ncm_base == ncm or any(p in desc_lower for p in regras['desc'].lower().split()):
                # Verifica condições (ex: "sem açúcar")
                if 'condicoes' in regras and not all(c in desc_lower for c in regras['condicoes']):
                    continue
                return {'tipo': 'reduzido', 'regras': regras}
        
        # 4. Padrão (alíquota normal)
        return {'tipo': 'padrao', 'regras': {'aliq': self.aliquota_padrao}}

    def calcular_icms_cesta_basica(self, produto: Produto, uf_origem: str) -> float:
        """Calcula o valor do ICMS conforme as regras da cesta básica"""
        categoria = self.get_categoria_produto(produto)
        valor_pauta = self._obter_valor_pauta(produto)
        valor_tributavel = valor_pauta if valor_pauta else produto.valor_total
        
        if categoria['tipo'] == 'seletivo':
            return valor_tributavel * categoria['regras']['aliq'] / 100
        
        elif categoria['tipo'] == 'zero':
            if callable(categoria['regras']['aliq']):  # Tratamento especial (feijão)
                aliquota = categoria['regras']['aliq'](uf_origem)
                return valor_tributavel * aliquota / 100
            return 0.0
        
        elif categoria['tipo'] == 'reduzido':
            return valor_tributavel * categoria['regras']['aliq'] / 100
        
        return valor_tributavel * self.aliquota_padrao / 100  # Padrão

    def _obter_valor_pauta(self, produto: Produto) -> Optional[float]:
        """Obtém valor da pauta fiscal se existir"""
        if produto.cest and produto.cest in self.pautas:
            return self.pautas[produto.cest]
        if produto.ncm in self.pautas:
            return self.pautas[produto.ncm]
        return None