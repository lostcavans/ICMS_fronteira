from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class RegimeTributario(str, Enum):
    SIMPLES = "simples"
    SIMPLES_EXCEDENTE = "simples_excedente"
    NORMAL = "normal"

class Produto(BaseModel):
    item: str
    codigo: str
    descricao: str
    ncm: str
    cest: Optional[str] = None
    cfop: str
    unidade: str
    quantidade: float
    valor_unitario: float
    valor_total: float
    valor_ipi: float = 0.0
    valor_icms: float = 0.0
    valor_frete: float = 0.0
    valor_seguro: float = 0.0
    valor_desconto: float = 0.0
    aliquota_icms: Optional[float] = None

class Impostos(BaseModel):
    aliquota_interna: float = Field(20.5, description="Alíquota interna do ICMS (%)")
    aliquota_interestadual: float = Field(..., description="Alíquota interestadual (%)")
    mva_original: Optional[float] = Field(None, description="MVA Original (%)")
    mva_cnae: Optional[float] = Field(None, description="MVA CNAE (%)")
    difal: Optional[float] = Field(None, description="DIFAL (%)")
    aliquota_credito: Optional[float] = Field(None, description="Alíquota de crédito (%)")
    aliquota_reducao: Optional[float] = Field(None, description="Alíquota de redução (%)")

class NotaFiscal(BaseModel):
    chave: str
    numero: str
    emitente_cnpj: str
    emitente_nome: str
    destinatario_nome: str
    emitente_regime: RegimeTributario
    emitente_uf: str
    destinatario_uf: str
    produtos: List[Produto]
    valor_total: float
    valor_frete: float = 0.0
    valor_seguro: float = 0.0
    valor_desconto: float = 0.0
    valor_ipi: float = 0.0
    valor_icms: float = 0.0
    aliquota_interestadual: float = 0.0