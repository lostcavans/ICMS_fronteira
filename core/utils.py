import json
from pathlib import Path
from typing import Dict, Any

def carregar_configuracao(caminho: Path) -> Dict[str, Any]:
    """Carrega um arquivo de configuração JSON"""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Arquivo de configuração não encontrado: {caminho}")
    except json.JSONDecodeError:
        raise ValueError(f"Erro ao decodificar o arquivo JSON: {caminho}")

def salvar_configuracao(caminho: Path, dados: Dict[str, Any]):
    """Salva um dicionário como arquivo JSON"""
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def formatar_moeda(valor: float) -> str:
    """Formata um valor float como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def validar_cnpj(cnpj: str) -> bool:
    """Valida um CNPJ"""
    cnpj = ''.join(filter(str.isdigit, cnpj))
    
    if len(cnpj) != 14:
        return False
    
    # Cálculo do primeiro dígito verificador
    soma = 0
    peso = 5
    for i in range(12):
        soma += int(cnpj[i]) * peso
        peso -= 1
        if peso == 1:
            peso = 9
    
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Cálculo do segundo dígito verificador
    soma = 0
    peso = 6
    for i in range(13):
        soma += int(cnpj[i]) * peso
        peso -= 1
        if peso == 1:
            peso = 9
    
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cnpj[12]) == digito1 and int(cnpj[13]) == digito2