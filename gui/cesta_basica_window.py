from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QPushButton, QGroupBox, QMessageBox, QFileDialog, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from core.models import NotaFiscal
from core.cesta_basica import CestaBasicaCalculator

class CestaBasicaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_nota = None
        self.calculator = CestaBasicaCalculator()
        self._setup_ui()
    
    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Tabela de produtos
        self.table_produtos = QTableWidget()
        self.table_produtos.setColumnCount(7)
        self.table_produtos.setHorizontalHeaderLabels([
            "Item", "Descrição", "NCM", "CEST", "Valor", 
            "Cesta Básica", "ICMS"
        ])
        self.table_produtos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table_produtos)
        
        # Grupo de resultados
        self.result_group = QGroupBox("Resultados")
        self.result_layout = QFormLayout()
        
        self.lbl_total_itens = QLabel("0")
        self.lbl_total_cesta = QLabel("0")
        self.lbl_total_icms = QLabel("R$ 0,00")
        self.lbl_economia = QLabel("R$ 0,00")
        
        self.result_layout.addRow("Total de Itens:", self.lbl_total_itens)
        self.result_layout.addRow("Itens da Cesta Básica:", self.lbl_total_cesta)
        self.result_layout.addRow("ICMS Total:", self.lbl_total_icms)
        self.result_layout.addRow("Economia Estimada:", self.lbl_economia)
        
        self.result_group.setLayout(self.result_layout)
        self.layout.addWidget(self.result_group)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        self.btn_todos = QPushButton(QIcon(":/icons/all.png"), " Mostrar Todos")
        self.btn_todos.clicked.connect(self.mostrar_todos)
        
        self.btn_filtrar = QPushButton(QIcon(":/icons/filter.png"), " Filtrar Cesta")
        self.btn_filtrar.clicked.connect(self.filtrar_cesta)
        
        self.btn_exportar = QPushButton(QIcon(":/icons/export.png"), " Exportar")
        self.btn_exportar.clicked.connect(self.exportar_dados)
        
        btn_layout.addWidget(self.btn_todos)
        btn_layout.addWidget(self.btn_filtrar)
        btn_layout.addWidget(self.btn_exportar)
        
        self.layout.addLayout(btn_layout)
    
    def set_nota(self, nota: NotaFiscal):
        self.current_nota = nota
        self.table_produtos.setRowCount(len(nota.produtos))
        
        total_cesta = 0
        total_icms = 0.0
        economia = 0.0
        
        for row, produto in enumerate(nota.produtos):
            # Preenche dados básicos do produto
            self.table_produtos.setItem(row, 0, QTableWidgetItem(produto.item))
            self.table_produtos.setItem(row, 1, QTableWidgetItem(produto.descricao))
            self.table_produtos.setItem(row, 2, QTableWidgetItem(produto.ncm))
            self.table_produtos.setItem(row, 3, QTableWidgetItem(produto.cest if produto.cest else ""))
            self.table_produtos.setItem(row, 4, QTableWidgetItem(f"R$ {produto.valor_total:,.2f}"))
            
            # Verifica se é cesta básica
            is_cesta = self.calculator.is_cesta_basica(produto)
            self.table_produtos.setItem(row, 5, QTableWidgetItem("✔" if is_cesta else ""))
            
            # Calcula ICMS conforme regras
            if is_cesta:
                icms = self.calculator.calcular_icms_cesta_basica(produto, nota.emitente_uf)
                total_cesta += 1
                # Calcula economia (diferença entre ICMS normal e ICMS cesta básica)
                economia += max(0, produto.valor_icms - icms)
            else:
                icms = produto.valor_icms
            
            self.table_produtos.setItem(row, 6, QTableWidgetItem(f"R$ {icms:,.2f}"))
            total_icms += icms
        
        # Atualiza totais
        self.lbl_total_itens.setText(str(len(nota.produtos)))
        self.lbl_total_cesta.setText(str(total_cesta))
        self.lbl_total_icms.setText(f"R$ {total_icms:,.2f}")
        self.lbl_economia.setText(f"R$ {economia:,.2f}")
        
        # Aplica formatação condicional
        self._aplicar_formatacao()
    
    def _aplicar_formatacao(self):
        """Aplica formatação condicional na tabela"""
        for row in range(self.table_produtos.rowCount()):
            # Destaque para itens da cesta básica
            if self.table_produtos.item(row, 5).text() == "✔":
                for col in range(self.table_produtos.columnCount()):
                    self.table_produtos.item(row, col).setBackground(Qt.lightGray)
    
    def mostrar_todos(self):
        """Mostra todos os itens, independente de serem da cesta básica"""
        if self.current_nota:
            self.set_nota(self.current_nota)
    
    def filtrar_cesta(self):
        """Mostra apenas os itens da cesta básica"""
        if not self.current_nota:
            return
            
        for row in range(self.table_produtos.rowCount()):
            is_visible = self.table_produtos.item(row, 5).text() == "✔"
            self.table_produtos.setRowHidden(row, not is_visible)
    
    def exportar_dados(self):
        """Exporta os dados para CSV"""
        if not self.current_nota:
            QMessageBox.warning(self, "Aviso", "Nenhuma nota fiscal carregada")
            return
            
        from pathlib import Path
        import csv
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Dados", "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # Escreve cabeçalho
                header = []
                for col in range(self.table_produtos.columnCount()):
                    header.append(self.table_produtos.horizontalHeaderItem(col).text())
                writer.writerow(header)
                
                # Escreve dados
                for row in range(self.table_produtos.rowCount()):
                    if not self.table_produtos.isRowHidden(row):
                        row_data = []
                        for col in range(self.table_produtos.columnCount()):
                            item = self.table_produtos.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Sucesso", "Dados exportados com sucesso!")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar dados:\n{str(e)}")
    
    def limpar_dados(self):
        self.current_nota = None
        self.table_produtos.setRowCount(0)
        self.lbl_total_itens.setText("0")
        self.lbl_total_cesta.setText("0")
        self.lbl_total_icms.setText("R$ 0,00")
        self.lbl_economia.setText("R$ 0,00")