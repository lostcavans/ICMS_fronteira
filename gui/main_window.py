# main_window.py
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QWidget, 
                            QLabel, QFormLayout, QGroupBox, QPushButton, 
                            QFileDialog, QMessageBox, QScrollArea, QVBoxLayout,
                            QComboBox, QLineEdit, QDateEdit, QListWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from gui.calculation_window import CalculationWindow
from gui.cesta_basica_window import CestaBasicaWindow
from gui.history_window import HistoryWindow
from core.models import NotaFiscal
from core.xml_processor import XMLProcessor
from core.config_manager import ConfigManager
import os
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_nota = None
        self.xml_processor = XMLProcessor()
        self.config = ConfigManager()
        self._setup_ui()
        self._load_empresas()
    
    def _setup_ui(self):
        self.setWindowTitle("Sistema de ICMS Fronteira")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Barra superior com seletores
        top_bar = QWidget()
        top_layout = QFormLayout()
        top_bar.setLayout(top_layout)
        
        # Seleção de empresa
        self.cmb_empresa = QComboBox()
        self.cmb_empresa.setEditable(True)
        self.cmb_empresa.setPlaceholderText("Selecione a empresa")
        top_layout.addRow("Empresa:", self.cmb_empresa)
        
        # Seleção de ano e competência
        self.txt_ano = QLineEdit(QDate.currentDate().toString("yyyy"))
        self.txt_ano.setMaximumWidth(60)
        
        self.date_competencia = QDateEdit()
        self.date_competencia.setDisplayFormat("MM/yyyy")
        self.date_competencia.setDate(QDate.currentDate())
        
        competencia_layout = QVBoxLayout()
        competencia_layout.addWidget(QLabel("Ano:"))
        competencia_layout.addWidget(self.txt_ano)
        competencia_layout.addSpacing(20)
        competencia_layout.addWidget(QLabel("Competência:"))
        competencia_layout.addWidget(self.date_competencia)
        competencia_layout.addStretch()
        
        top_layout.addRow(competencia_layout)
        main_layout.addWidget(top_bar)
        
        # Lista de notas fiscais
        self.lst_notas = QListWidget()
        self.lst_notas.itemDoubleClicked.connect(self.abrir_nota)
        main_layout.addWidget(QLabel("Notas Fiscais:"))
        main_layout.addWidget(self.lst_notas)
        
        # Barra de botões
        btn_bar = QWidget()
        btn_layout = QVBoxLayout()
        btn_bar.setLayout(btn_layout)
        
        self.btn_carregar = QPushButton(QIcon(":/icons/open.png"), " Carregar NFe")
        self.btn_carregar.clicked.connect(self.carregar_nota)
        
        self.btn_novo = QPushButton(QIcon(":/icons/new.png"), " Novo Cálculo")
        self.btn_novo.clicked.connect(self.novo_calculo)
        
        self.btn_historico = QPushButton(QIcon(":/icons/history.png"), " Ver Histórico")
        self.btn_historico.clicked.connect(self.ver_historico)
        
        self.btn_limpar = QPushButton(QIcon(":/icons/clear.png"), " Limpar")
        self.btn_limpar.clicked.connect(self.limpar_dados)
        
        btn_layout.addWidget(self.btn_carregar)
        btn_layout.addWidget(self.btn_novo)
        btn_layout.addWidget(self.btn_historico)
        btn_layout.addWidget(self.btn_limpar)
        btn_layout.addStretch()
        
        main_layout.addWidget(btn_bar)
        
        # Abas principais
        self.tabs = QTabWidget()
        self.calculation_tab = CalculationWindow()
        self.cesta_basica_tab = CestaBasicaWindow()
        self.history_tab = HistoryWindow()
        
        self.tabs.addTab(self.calculation_tab, "Cálculos ICMS")
        self.tabs.addTab(self.cesta_basica_tab, "Cesta Básica")
        self.tabs.addTab(self.history_tab, "Histórico")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("Pronto para carregar NFe")
        
        # Carrega as notas da pasta padrão
        self._carregar_notas_pasta()
    
    def _load_empresas(self):
        """Carrega a lista de empresas do diretório fiscal"""
        empresas_dir = Path("Z:/Fiscal/Simples Nacional/")
        if empresas_dir.exists():
            empresas = [d.name for d in empresas_dir.iterdir() if d.is_dir()]
            self.cmb_empresa.addItems(empresas)
    
    def _carregar_notas_pasta(self):
        """Carrega as notas da pasta selecionada"""
        empresa = self.cmb_empresa.currentText()
        competencia = self.date_competencia.date().toString("MM.yyyy")
        
        if not empresa:
            return
            
        notas_dir = Path(f"Z:/Fiscal/Simples Nacional/{empresa}/notas/{competencia}")
        if notas_dir.exists():
            self.lst_notas.clear()
            for xml_file in notas_dir.glob("*.xml"):
                self.lst_notas.addItem(xml_file.name)
    
    def carregar_nota(self):
        """Carrega um arquivo XML de NFe e atualiza a interface"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar NFe", 
            "", "Arquivos XML (*.xml);;Todos os arquivos (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                nota = self.xml_processor.parse_xml(xml_content)
                self.set_nota(nota)
                
                self.statusBar().showMessage(f"NFe {nota.numero} carregada com sucesso", 3000)
                QMessageBox.information(self, "Sucesso", "NFe processada com sucesso!")
                
            except Exception as e:
                self.statusBar().showMessage("Erro ao processar NFe", 3000)
                QMessageBox.critical(self, "Erro", f"Falha ao processar NFe:\n{str(e)}")
    
    def abrir_nota(self, item):
        """Abre a nota selecionada na lista"""
        empresa = self.cmb_empresa.currentText()
        competencia = self.date_competencia.date().toString("MM.yyyy")
        xml_path = Path(f"Z:/Fiscal/Simples Nacional/{empresa}/notas/{competencia}/{item.text()}")
        
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            nota = self.xml_processor.parse_xml(xml_content)
            self.set_nota(nota)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao abrir NFe:\n{str(e)}")
    
    def novo_calculo(self):
        """Prepara a interface para um novo cálculo"""
        self.limpar_dados()
        self.tabs.setCurrentIndex(0)  # Vai para a aba de cálculos
    
    def ver_historico(self):
        """Exibe o histórico de cálculos"""
        if self.current_nota:
            self.history_tab.carregar_historico(self.current_nota.chave)
            self.tabs.setCurrentIndex(2)  # Vai para a aba de histórico
    
    def limpar_dados(self):
        """Limpa todos os dados exibidos"""
        self.current_nota = None
        self.calculation_tab.limpar_dados()
        self.cesta_basica_tab.limpar_dados()
        self.history_tab.limpar_dados()
        self.statusBar().showMessage("Dados limpos", 2000)
    
    def set_nota(self, nota: NotaFiscal):
        """Atualiza a interface com os dados da nota fiscal"""
        self.current_nota = nota
        self.calculation_tab.set_nota(nota)
        self.cesta_basica_tab.set_nota(nota)