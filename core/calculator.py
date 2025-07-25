from .models import *
from typing import Optional
from core.models import Impostos, Produto, RegimeTributario

class ICMSCalculator:
    @staticmethod
    def calcular_mva_ajustada(impostos: Impostos) -> float:
        """Calcula o MVA ajustado"""
        if not impostos.mva_original:
            return 0.0
        return ((1 - impostos.aliquota_interestadual/100) / 
               (1 - impostos.aliquota_interna/100) * 
               (1 + impostos.mva_original/100) - 1) * 100

    @staticmethod
    def calcular_icms_st(produto: Produto, impostos: Impostos, regime: RegimeTributario, considerar_desconto: bool = True) -> float:
        """Calcula o ICMS ST conforme regime tributário"""
        base_st = (produto.valor_total + 
                  produto.valor_ipi + 
                  produto.valor_frete + 
                  produto.valor_seguro)
        
        if considerar_desconto:
            base_st -= produto.valor_desconto
        
        if regime == RegimeTributario.NORMAL:
            mva_ajustada = ICMSCalculator.calcular_mva_ajustada(impostos)
            base_st *= (1 + mva_ajustada/100)
        else:
            base_st *= (1 + (impostos.mva_original or 0)/100)
            
        icms_st = base_st * (impostos.aliquota_interna/100)
        icms_destacado = ICMSCalculator.calcular_icms_destacado(produto, impostos, considerar_desconto)
        
        return max(0, icms_st - icms_destacado)

    @staticmethod
    def calcular_icms_tributado(produto: Produto, impostos: Impostos, regime: RegimeTributario, usar_credito_manual: bool = False) -> float:
        """Calcula o ICMS tributado conforme regime"""
        base = (produto.valor_total + 
               produto.valor_ipi + 
               produto.valor_frete + 
               produto.valor_seguro)
        
        if regime in [RegimeTributario.SIMPLES, RegimeTributario.SIMPLES_EXCEDENTE]:
            if impostos.difal:
                return base / (1 - impostos.aliquota_interna/100) * (impostos.difal/100)
            return base / (1 - impostos.aliquota_interna/100) * (
                   impostos.aliquota_interna/100 - impostos.aliquota_interestadual/100)
        else:
            return (base / (1 - impostos.aliquota_interna/100) * 
                   (1 + (impostos.mva_cnae or 0)/100) * 
                   (impostos.aliquota_interna/100) - 
                   ICMSCalculator.calcular_icms_destacado(produto, impostos, usar_credito_manual))
            
    @staticmethod
    def calcular_icms_destacado(produto: Produto, impostos: Impostos, considerar_desconto: bool) -> float:
        """Calcula o ICMS destacado considerando benefícios fiscais e a regra do menor valor"""
        base_calculo = produto.valor_total
        if considerar_desconto:
            base_calculo -= produto.valor_desconto
        
        # Calcula ambos os valores
        valor_por_aliquota = base_calculo * (impostos.aliquota_interestadual/100)
        valor_picms = produto.valor_icms
        
        # Aplica a regra do menor valor
        icms_destacado = min(valor_por_aliquota, valor_picms)
        
        # Aplica benefícios fiscais se existirem
        if impostos.aliquota_reducao and impostos.aliquota_reducao > 0:
            return icms_destacado * (impostos.aliquota_reducao/100)
        elif impostos.aliquota_credito and impostos.aliquota_credito > 0:
            return icms_destacado * (impostos.aliquota_credito/100)
        
        return icms_destacado