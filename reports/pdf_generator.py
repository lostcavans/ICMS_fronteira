from fpdf import FPDF
from datetime import datetime
from core.models import NotaFiscal, CalculoICMS
from typing import List

class PDFGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
    
    def generate_calculation_report(self, nota: NotaFiscal, calculos: List[CalculoICMS], output_path: str):
        """Gera um relatório PDF com os cálculos realizados"""
        self.pdf.add_page()
        
        # Cabeçalho
        self.pdf.set_font("Arial", 'B', 16)
        self.pdf.cell(0, 10, "Relatório de Cálculos de ICMS Fronteira", 0, 1, 'C')
        
        # Informações da nota
        self.pdf.set_font("Arial", '', 12)
        self.pdf.cell(0, 10, f"Nota Fiscal: {nota.chNFe}", 0, 1)
        self.pdf.cell(0, 10, f"Emitente: {nota.emitente_CNPJ}", 0, 1)
        self.pdf.cell(0, 10, f"Destinatário: {nota.dest_CNPJ} - {nota.dest_UF}", 0, 1)
        self.pdf.cell(0, 10, f"Data de Emissão: {nota.dhEmi.strftime('%d/%m/%Y')}", 0, 1)
        self.pdf.ln(10)
        
        # Cálculos
        self.pdf.set_font("Arial", 'B', 14)
        self.pdf.cell(0, 10, "Cálculos Realizados:", 0, 1)
        self.pdf.ln(5)
        
        for calculo in calculos:
            self.pdf.set_font("Arial", 'B', 12)
            self.pdf.cell(0, 10, f"Tipo: {calculo.tipo_calculo}", 0, 1)
            
            self.pdf.set_font("Arial", '', 10)
            self.pdf.cell(0, 10, f"Data do Cálculo: {calculo.data_calculo.strftime('%d/%m/%Y %H:%M:%S')}", 0, 1)
            self.pdf.cell(0, 10, f"Valor Calculado: R$ {calculo.valor_calculado:,.2f}", 0, 1)
            
            # Configurações
            self.pdf.cell(0, 10, "Configurações:", 0, 1)
            self.pdf.cell(0, 10, f"- Considerar desconto: {'Sim' if calculo.considerar_desconto else 'Não'}", 0, 1)
            self.pdf.cell(0, 10, f"- Usar crédito manual: {'Sim' if calculo.usar_credito_manual else 'Não'}", 0, 1)
            self.pdf.cell(0, 10, f"- MVA Original: {calculo.mva_original:.2f}%", 0, 1)
            self.pdf.cell(0, 10, f"- MVA CNAE: {calculo.mva_cnae:.2f}%", 0, 1)
            self.pdf.cell(0, 10, f"- Difal Simples: {calculo.difal:.2f}%", 0, 1)
            self.pdf.cell(0, 10, f"- Crédito ICMS: {calculo.credito_icms:.2f}%", 0, 1)
            self.pdf.cell(0, 10, f"- Alíquota Redução: {calculo.aliquota_reducao:.2f}%", 0, 1)
            self.pdf.cell(0, 10, f"- Alíquota Interna: {calculo.aliquota_interna:.2f}%", 0, 1)
            self.pdf.cell(0, 10, f"- Alíquota Interestadual: {calculo.aliquota_interestadual:.2f}%", 0, 1)
            
            # Fórmula
            self.pdf.cell(0, 10, "Fórmula Utilizada:", 0, 1)
            self.pdf.multi_cell(0, 10, calculo.formula_utilizada)
            
            self.pdf.ln(5)
            self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
            self.pdf.ln(5)
        
        # Rodapé
        self.pdf.set_y(-15)
        self.pdf.set_font("Arial", 'I', 8)
        self.pdf.cell(0, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 0, 'C')
        
        # Salva o PDF
        self.pdf.output(output_path)