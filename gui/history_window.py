# history_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QPushButton, QHBoxLayout, QMessageBox, 
                            QMenu, QAction, QFileDialog, QTextEdit, QDialog, 
                            QVBoxLayout, QTabWidget)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon
from fpdf import FPDF
import pandas as pd
import json
from pathlib import Path
import os

class DetalhesCalculoDialog(QDialog):
    """Janela modal para exibir detalhes completos do cálculo"""
    def __init__(self, calculo_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalhes do Cálculo")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        tabs = QTabWidget()
        
        # Tab Resumo
        tab_resumo = QWidget()
        resumo_layout = QVBoxLayout()
        self.txt_resumo = QTextEdit()
        self.txt_resumo.setReadOnly(True)
        resumo_layout.addWidget(self.txt_resumo)
        tab_resumo.setLayout(resumo_layout)
        
        # Tab Produtos
        tab_produtos = QWidget()
        produtos_layout = QVBoxLayout()
        self.table_produtos = QTableWidget()
        self.table_produtos.setColumnCount(8)
        self.table_produtos.setHorizontalHeaderLabels([
            "Item", "Descrição", "NCM", "CEST", "Valor", 
            "ICMS", "ST", "Tributado"
        ])
        produtos_layout.addWidget(self.table_produtos)
        tab_produtos.setLayout(produtos_layout)
        
        tabs.addTab(tab_resumo, "Resumo")
        tabs.addTab(tab_produtos, "Produtos")
        
        layout.addWidget(tabs)
        
        self.calcular_resumo(calculo_data)
        self.preencher_produtos(calculo_data.get('produtos', []))
    
    def calcular_resumo(self, calculo):
        resumo = f"""
        <h2>Resumo do Cálculo</h2>
        <p><b>Data/Hora:</b> {calculo.get('data', 'N/A')}</p>
        
        <h3>Parâmetros</h3>
        <table border="1" cellpadding="5">
            <tr>
                <td><b>Alíquota Interestadual:</b></td>
                <td>{calculo['parametros'].get('aliq_interestadual', '')}%</td>
                <td><b>Alíquota Interna:</b></td>
                <td>{calculo['parametros'].get('aliq_interna', '')}%</td>
            </tr>
            <tr>
                <td><b>MVA Original:</b></td>
                <td>{calculo['parametros'].get('mva_original', '')}%</td>
                <td><b>MVA CNAE:</b></td>
                <td>{calculo['parametros'].get('mva_cnae', '')}%</td>
            </tr>
            <tr>
                <td><b>DIFAL:</b></td>
                <td>{calculo['parametros'].get('difal', '')}%</td>
                <td><b>Crédito ICMS:</b></td>
                <td>{calculo['parametros'].get('aliq_credito', '')}%</td>
            </tr>
        </table>
        
        <h3>Resultados</h3>
        <table border="1" cellpadding="5">
            <tr>
                <td><b>ICMS ST:</b></td>
                <td>{calculo['resultados'].get('icms_st', '')}</td>
                <td><b>ICMS Tributado:</b></td>
                <td>{calculo['resultados'].get('icms_tributado', '')}</td>
            </tr>
            <tr>
                <td><b>ICMS Uso/Consumo:</b></td>
                <td>{calculo['resultados'].get('icms_uso_consumo', '')}</td>
                <td><b>ICMS Redução:</b></td>
                <td>{calculo['resultados'].get('icms_reducao', '')}</td>
            </tr>
        </table>
        """
        self.txt_resumo.setHtml(resumo)
    
    def preencher_produtos(self, produtos):
        self.table_produtos.setRowCount(len(produtos))
        for row, produto in enumerate(produtos):
            self.table_produtos.setItem(row, 0, QTableWidgetItem(produto.get('item', '')))
            self.table_produtos.setItem(row, 1, QTableWidgetItem(produto.get('descricao', '')))
            self.table_produtos.setItem(row, 2, QTableWidgetItem(produto.get('ncm', '')))
            self.table_produtos.setItem(row, 3, QTableWidgetItem(produto.get('cest', '')))
            self.table_produtos.setItem(row, 4, QTableWidgetItem(f"R$ {produto.get('valor_total', 0):,.2f}"))
            self.table_produtos.setItem(row, 5, QTableWidgetItem(f"R$ {produto.get('valor_icms', 0):,.2f}"))
            self.table_produtos.setItem(row, 6, QTableWidgetItem(f"R$ {produto.get('icms_st', 0):,.2f}"))
            self.table_produtos.setItem(row, 7, QTableWidgetItem(f"R$ {produto.get('icms_tributado', 0):,.2f}"))

class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_chave = None
        self.current_nota = None
        self._setup_ui()
    
    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Barra de ferramentas
        tool_bar = QWidget()
        tool_layout = QHBoxLayout()
        tool_bar.setLayout(tool_layout)
        
        self.btn_atualizar = QPushButton(QIcon(":/icons/refresh.png"), " Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_historico)
        
        self.btn_exportar = QPushButton(QIcon(":/icons/export.png"), " Exportar Completo")
        self.btn_exportar.clicked.connect(self.exportar_completo)
        
        self.btn_limpar = QPushButton(QIcon(":/icons/clear.png"), " Limpar")
        self.btn_limpar.clicked.connect(self.limpar_dados)
        
        tool_layout.addWidget(self.btn_atualizar)
        tool_layout.addWidget(self.btn_exportar)
        tool_layout.addWidget(self.btn_limpar)
        tool_layout.addStretch()
        
        self.layout.addWidget(tool_bar)
        
        # Tabela de histórico
        self.table_history = QTableWidget()
        self.table_history.setColumnCount(8)  # Coluna adicional para detalhes
        self.table_history.setHorizontalHeaderLabels([
            "Data/Hora", "Tipo", "ICMS ST", "ICMS Tributado", 
            "ICMS Uso/Consumo", "ICMS Redução", "Produtos", "Ações"
        ])
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_history.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_history.customContextMenuRequested.connect(self.mostrar_menu_contexto)
        
        self.layout.addWidget(self.table_history)
    
    def set_nota(self, nota):
        """Armazena a nota atual para referência nos relatórios"""
        self.current_nota = nota
    
    def mostrar_menu_contexto(self, pos):
        menu = QMenu()
        
        action_ver = QAction(QIcon(":/icons/view.png"), "Ver Detalhes", self)
        action_ver.triggered.connect(self.ver_detalhes)
        
        action_exportar = QAction(QIcon(":/icons/export.png"), "Exportar Este Cálculo", self)
        action_exportar.triggered.connect(self.exportar_calculo)
        
        menu.addAction(action_ver)
        menu.addAction(action_exportar)
        
        menu.exec_(self.table_history.viewport().mapToGlobal(pos))
    
    def carregar_historico(self, chave_nota: str = None):
        self.current_chave = chave_nota
        self.table_history.setRowCount(0)
        
        if not chave_nota:
            return
            
        arquivo = Path("calculos") / f"{chave_nota}.json"
        
        if not arquivo.exists():
            return
            
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            self.table_history.setRowCount(len(dados["calculos"]))
            
            for row, calculo in enumerate(dados["calculos"]):
                # Colunas básicas
                self.table_history.setItem(row, 0, QTableWidgetItem(calculo["data"]))
                self.table_history.setItem(row, 1, QTableWidgetItem("Completo"))
                self.table_history.setItem(row, 2, QTableWidgetItem(calculo["resultados"]["icms_st"]))
                self.table_history.setItem(row, 3, QTableWidgetItem(calculo["resultados"]["icms_tributado"]))
                self.table_history.setItem(row, 4, QTableWidgetItem(calculo["resultados"]["icms_uso_consumo"]))
                self.table_history.setItem(row, 5, QTableWidgetItem(calculo["resultados"]["icms_reducao"]))
                
                # Coluna de produtos (resumo)
                num_produtos = len(calculo.get('produtos', []))
                self.table_history.setItem(row, 6, QTableWidgetItem(f"{num_produtos} itens"))
                
                # Botão de ações
                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_widget.setLayout(btn_layout)
                
                btn_ver = QPushButton(QIcon(":/icons/view.png"), "")
                btn_ver.setToolTip("Ver detalhes")
                btn_ver.clicked.connect(lambda _, r=row: self.ver_detalhes(r))
                
                btn_exportar = QPushButton(QIcon(":/icons/export.png"), "")
                btn_exportar.setToolTip("Exportar cálculo")
                btn_exportar.clicked.connect(lambda _, r=row: self.exportar_calculo(r))
                
                btn_layout.addWidget(btn_ver)
                btn_layout.addWidget(btn_exportar)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.table_history.setCellWidget(row, 7, btn_widget)
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar histórico:\n{str(e)}")
    
    def ver_detalhes(self, row):
        item = self.table_history.item(row, 0)
        chave = self.current_chave
        data = item.text()
        
        arquivo = Path("calculos") / f"{chave}.json"
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            calculo = next((c for c in dados["calculos"] if c["data"] == data), None)
            
            if calculo:
                dialog = DetalhesCalculoDialog(calculo, self)
                dialog.exec_()
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exibir detalhes:\n{str(e)}")
    
    def exportar_completo(self):
        """Exporta todo o histórico da nota"""
        if not self.current_chave:
            QMessageBox.warning(self, "Aviso", "Nenhuma nota fiscal selecionada")
            return
            
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Histórico Completo", "",
            "PDF Files (*.pdf);;Excel Files (*.xlsx);;JSON Files (*.json)",
            options=options
        )
        
        if not file_path:
            return
            
        try:
            arquivo = Path("calculos") / f"{self.current_chave}.json"
            
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            if file_path.endswith('.pdf'):
                self._exportar_pdf_completo(file_path, dados)
            elif file_path.endswith('.xlsx'):
                self._exportar_excel_completo(file_path, dados)
            elif file_path.endswith('.json'):
                self._exportar_json(file_path, dados)
            
            QMessageBox.information(self, "Sucesso", "Histórico exportado com sucesso!")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar histórico:\n{str(e)}")
    
    def exportar_calculo(self, row):
        """Exporta um cálculo específico"""
        item = self.table_history.item(row, 0)
        chave = self.current_chave
        data = item.text()
        
        arquivo = Path("calculos") / f"{chave}.json"
        
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            calculo = next((c for c in dados["calculos"] if c["data"] == data), None)
            
            if not calculo:
                return
                
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"Exportar Cálculo {data}", "",
                "PDF Files (*.pdf);;Excel Files (*.xlsx);;JSON Files (*.json)",
                options=options
            )
            
            if not file_path:
                return
                
            if file_path.endswith('.pdf'):
                self._exportar_pdf_calculo(file_path, calculo)
            elif file_path.endswith('.xlsx'):
                self._exportar_excel_calculo(file_path, calculo)
            elif file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(calculo, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Sucesso", "Cálculo exportado com sucesso!")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar cálculo:\n{str(e)}")
    
    def _exportar_pdf_completo(self, file_path, dados):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Cabeçalho com dados da nota
        if self.current_nota:
            pdf.cell(200, 10, txt=f"Relatório Completo - NFe {self.current_nota.numero}", ln=1, align='C')
            pdf.cell(200, 10, txt=f"Emitente: {self.current_nota.emitente_nome}", ln=1)
            pdf.cell(200, 10, txt=f"Destinatário: {self.current_nota.destinatario_nome}", ln=1)
            pdf.ln(10)
        
        for calculo in dados["calculos"]:
            self._adicionar_calculo_pdf(pdf, calculo)
            pdf.ln(5)
            pdf.cell(200, 10, txt="-"*50, ln=1)
            pdf.ln(5)
        
        pdf.output(file_path)
    
    def _exportar_pdf_calculo(self, file_path, calculo):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        if self.current_nota:
            pdf.cell(200, 10, txt=f"Relatório de Cálculo - NFe {self.current_nota.numero}", ln=1, align='C')
            pdf.cell(200, 10, txt=f"Data: {calculo['data']}", ln=1)
            pdf.ln(10)
        
        self._adicionar_calculo_pdf(pdf, calculo)
        pdf.output(file_path)
    
    def _adicionar_calculo_pdf(self, pdf, calculo):
        """Adiciona um cálculo ao PDF com formatação"""
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"Cálculo: {calculo['data']}", ln=1)
        pdf.set_font("Arial", size=10)
        
        # Parâmetros
        pdf.cell(200, 10, txt="Parâmetros:", ln=1)
        pdf.cell(100, 8, txt=f"Alíquota Interestadual: {calculo['parametros']['aliq_interestadual']}%", ln=0)
        pdf.cell(100, 8, txt=f"Alíquota Interna: {calculo['parametros']['aliq_interna']}%", ln=1)
        pdf.cell(100, 8, txt=f"MVA Original: {calculo['parametros']['mva_original']}%", ln=0)
        pdf.cell(100, 8, txt=f"MVA CNAE: {calculo['parametros']['mva_cnae']}%", ln=1)
        pdf.ln(5)
        
        # Resultados
        pdf.cell(200, 10, txt="Resultados:", ln=1)
        pdf.cell(100, 8, txt=f"ICMS ST: {calculo['resultados']['icms_st']}", ln=0)
        pdf.cell(100, 8, txt=f"ICMS Tributado: {calculo['resultados']['icms_tributado']}", ln=1)
        pdf.cell(100, 8, txt=f"ICMS Uso/Consumo: {calculo['resultados']['icms_uso_consumo']}", ln=0)
        pdf.cell(100, 8, txt=f"ICMS Redução: {calculo['resultados']['icms_reducao']}", ln=1)
        pdf.ln(10)
        
        # Produtos (se existirem)
        if 'produtos' in calculo and calculo['produtos']:
            pdf.cell(200, 10, txt="Produtos:", ln=1)
            
            # Cabeçalho da tabela
            pdf.set_font("Arial", 'B', 8)
            col_widths = [15, 60, 20, 20, 25, 25, 25]
            headers = ["Item", "Descrição", "NCM", "CEST", "Valor", "ICMS", "ST"]
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, border=1)
            pdf.ln()
            
            # Dados dos produtos
            pdf.set_font("Arial", size=8)
            for produto in calculo['produtos']:
                pdf.cell(col_widths[0], 8, produto.get('item', ''), border=1)
                pdf.cell(col_widths[1], 8, produto.get('descricao', ''), border=1)
                pdf.cell(col_widths[2], 8, produto.get('ncm', ''), border=1)
                pdf.cell(col_widths[3], 8, produto.get('cest', ''), border=1)
                pdf.cell(col_widths[4], 8, f"R$ {produto.get('valor_total', 0):,.2f}", border=1)
                pdf.cell(col_widths[5], 8, f"R$ {produto.get('valor_icms', 0):,.2f}", border=1)
                pdf.cell(col_widths[6], 8, f"R$ {produto.get('icms_st', 0):,.2f}", border=1)
                pdf.ln()
    
    def _exportar_excel_completo(self, file_path, dados):
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Planilha de resumo
            resumo_data = []
            for calculo in dados["calculos"]:
                resumo_data.append({
                    "Data": calculo["data"],
                    "ICMS ST": calculo["resultados"]["icms_st"],
                    "ICMS Tributado": calculo["resultados"]["icms_tributado"],
                    "ICMS Uso/Consumo": calculo["resultados"]["icms_uso_consumo"],
                    "ICMS Redução": calculo["resultados"]["icms_reducao"],
                    "Nº Produtos": len(calculo.get("produtos", []))
                })
            
            pd.DataFrame(resumo_data).to_excel(writer, sheet_name="Resumo", index=False)
            
            # Planilha detalhada por cálculo
            for calculo in dados["calculos"]:
                if 'produtos' in calculo:
                    sheet_name = f"Cálculo {calculo['data'][:16]}"
                    produtos_data = []
                    for produto in calculo['produtos']:
                        produtos_data.append({
                            "Item": produto.get('item', ''),
                            "Descrição": produto.get('descricao', ''),
                            "NCM": produto.get('ncm', ''),
                            "CEST": produto.get('cest', ''),
                            "Valor": produto.get('valor_total', 0),
                            "ICMS": produto.get('valor_icms', 0),
                            "ICMS ST": produto.get('icms_st', 0),
                            "ICMS Tributado": produto.get('icms_tributado', 0)
                        })
                    
                    pd.DataFrame(produtos_data).to_excel(
                        writer, 
                        sheet_name=sheet_name[:31],  # Limite de caracteres do Excel
                        index=False
                    )
    
    def _exportar_excel_calculo(self, file_path, calculo):
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Planilha de parâmetros
            parametros_data = [{
                "Parâmetro": "Alíquota Interestadual",
                "Valor": f"{calculo['parametros']['aliq_interestadual']}%"
            }, {
                "Parâmetro": "Alíquota Interna",
                "Valor": f"{calculo['parametros']['aliq_interna']}%"
            }]  # Adicione todos os parâmetros
            
            pd.DataFrame(parametros_data).to_excel(
                writer, 
                sheet_name="Parâmetros", 
                index=False
            )
            
            # Planilha de resultados
            resultados_data = [{
                "Tipo": "ICMS ST",
                "Valor": calculo["resultados"]["icms_st"]
            }, {
                "Tipo": "ICMS Tributado",
                "Valor": calculo["resultados"]["icms_tributado"]
            }]  # Adicione todos os resultados
            
            pd.DataFrame(resultados_data).to_excel(
                writer, 
                sheet_name="Resultados", 
                index=False
            )
            
            # Planilha de produtos (se existir)
            if 'produtos' in calculo:
                produtos_data = []
                for produto in calculo['produtos']:
                    produtos_data.append({
                        "Item": produto.get('item', ''),
                        "Descrição": produto.get('descricao', ''),
                        "NCM": produto.get('ncm', ''),
                        "CEST": produto.get('cest', ''),
                        "Valor": f"R$ {produto.get('valor_total', 0):,.2f}",
                        "ICMS": f"R$ {produto.get('valor_icms', 0):,.2f}",
                        "ICMS ST": f"R$ {produto.get('icms_st', 0):,.2f}",
                        "ICMS Tributado": f"R$ {produto.get('icms_tributado', 0):,.2f}"
                    })
                
                pd.DataFrame(produtos_data).to_excel(
                    writer, 
                    sheet_name="Produtos", 
                    index=False
                )
    
    def _exportar_json(self, file_path, dados):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    
    def limpar_dados(self):
        self.current_chave = None
        self.current_nota = None
        self.table_history.setRowCount(0)