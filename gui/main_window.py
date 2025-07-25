# main_window.py
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, 
                            QLabel, QFormLayout, QGroupBox, QPushButton, 
                            QFileDialog, QMessageBox, QScrollArea,
                            QComboBox, QLineEdit, QDateEdit, QListWidget,
                            QListWidgetItem)

from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QIcon
from gui.calculation_window import CalculationWindow
from gui.cesta_basica_window import CestaBasicaWindow
from gui.history_window import HistoryWindow
from core.models import NotaFiscal
from core.xml_processor import XMLProcessor
from core.config_manager import ConfigManager
from pathlib import Path
import json
import os

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
        main_layout = QVBoxLayout(central_widget)

        # ====== TOPO: FILTROS ======
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QHBoxLayout()
        filtros_group.setLayout(filtros_layout)

        # Empresa
        self.cmb_empresa = QComboBox()
        self.cmb_empresa.setEditable(True)
        self.cmb_empresa.setPlaceholderText("Selecione a empresa")
        self.cmb_empresa.setMaximumWidth(250)

        # Ano
        self.txt_ano = QLineEdit(QDate.currentDate().toString("yyyy"))
        self.txt_ano.setMaximumWidth(80)

        # Competência
        self.date_competencia = QDateEdit()
        self.date_competencia.setDisplayFormat("MM/yyyy")
        self.date_competencia.setDate(QDate.currentDate())
        self.date_competencia.setMaximumWidth(100)

        # Adiciona ao layout
        filtros_layout.addWidget(QLabel("Empresa:"))
        filtros_layout.addWidget(self.cmb_empresa)
        filtros_layout.addSpacing(20)
        filtros_layout.addWidget(QLabel("Ano:"))
        filtros_layout.addWidget(self.txt_ano)
        filtros_layout.addSpacing(20)
        filtros_layout.addWidget(QLabel("Competência:"))
        filtros_layout.addWidget(self.date_competencia)
        filtros_layout.addStretch()

        main_layout.addWidget(filtros_group)

        # ====== CORPO PRINCIPAL ======
        corpo_layout = QHBoxLayout()

        # Lista de notas fiscais
        lista_group = QGroupBox("Notas Fiscais")
        lista_layout = QVBoxLayout()
        lista_group.setLayout(lista_layout)

        # Campo de busca
        self.txt_busca = QLineEdit()
        self.txt_busca.setPlaceholderText("Filtrar notas...")
        self.txt_busca.textChanged.connect(self._filtrar_lista)
        lista_layout.addWidget(self.txt_busca)

        self.lst_notas = QListWidget()
        self.lst_notas.itemDoubleClicked.connect(self.abrir_nota)
        lista_layout.addWidget(self.lst_notas)

        # Botão remover
        self.btn_remover = QPushButton("Remover selecionado")
        self.btn_remover.clicked.connect(self._remover_item)
        lista_layout.addWidget(self.btn_remover)

        corpo_layout.addWidget(lista_group, 2)  # 2 = peso maior para lista

        # Botões
        botoes_group = QGroupBox("Ações")
        botoes_layout = QVBoxLayout()
        botoes_group.setLayout(botoes_layout)

        self.btn_carregar = QPushButton(QIcon(":/icons/open.png"), " Carregar NFe")
        self.btn_carregar.clicked.connect(self.carregar_nota)

        self.btn_novo = QPushButton(QIcon(":/icons/new.png"), " Novo Cálculo")
        self.btn_novo.clicked.connect(self.novo_calculo)

        self.btn_historico = QPushButton(QIcon(":/icons/history.png"), " Ver Histórico")
        self.btn_historico.clicked.connect(self.ver_historico)

        self.btn_limpar = QPushButton(QIcon(":/icons/clear.png"), " Limpar")
        self.btn_limpar.clicked.connect(self.limpar_dados)

        botoes_layout.addWidget(self.btn_carregar)
        botoes_layout.addWidget(self.btn_novo)
        botoes_layout.addWidget(self.btn_historico)
        botoes_layout.addWidget(self.btn_limpar)
        botoes_layout.addStretch()

        corpo_layout.addWidget(botoes_group, 1)  # peso menor para botões

        main_layout.addLayout(corpo_layout)

        # ====== ABAS ======
        self.tabs = QTabWidget()
        self.calculation_tab = CalculationWindow()
        self.cesta_basica_tab = CestaBasicaWindow()
        self.history_tab = HistoryWindow()

        self.tabs.addTab(self.calculation_tab, "Cálculos ICMS")
        self.tabs.addTab(self.cesta_basica_tab, "Cesta Básica")
        self.tabs.addTab(self.history_tab, "Histórico")

        main_layout.addWidget(self.tabs)

        # ====== STATUS BAR ======
        self.statusBar().showMessage("Pronto para carregar NFe")

        # Conexões
        self.cmb_empresa.currentTextChanged.connect(self._carregar_notas_pasta)
        self.date_competencia.dateChanged.connect(self._carregar_notas_pasta)
    
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
        calculos_dir = Path("calculos")
        
        self.lst_notas.clear()
        
        # 1. Carrega XMLs da pasta de notas
        if notas_dir.exists():
            for xml_file in notas_dir.glob("*.xml"):
                item = QListWidgetItem(f"📄 {xml_file.name}")
                item.setData(Qt.UserRole, {"tipo": "xml", "path": str(xml_file)})
                item.setToolTip(f"Nota Fiscal Original\n{xml_file.name}")
                self.lst_notas.addItem(item)
        
        # 2. Carrega cálculos salvos
        if calculos_dir.exists():
            for json_file in calculos_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                        if dados.get("calculos"):
                            ultimo_calculo = dados["calculos"][-1]
                            emitente = ultimo_calculo.get("emitente", {}).get("nome", "NFe")
                            data = QDateTime.fromString(ultimo_calculo.get("data", ""), Qt.ISODate).toString("dd/MM/yyyy")
                            
                            item = QListWidgetItem(f"📊 {emitente} - {json_file.name}")
                            item.setData(Qt.UserRole, {"tipo": "calculo", "path": str(json_file)})
                            item.setToolTip(f"Cálculo Salvo\nEmitente: {emitente}\nData: {data}\nArquivo: {json_file.name}")
                            self.lst_notas.addItem(item)
                except Exception as e:
                    print(f"Erro ao carregar {json_file}: {str(e)}")
    
    def _filtrar_lista(self, texto):
        """Filtra a lista de notas conforme texto digitado"""
        for i in range(self.lst_notas.count()):
            item = self.lst_notas.item(i)
            item.setHidden(texto.lower() not in item.text().lower())
    
    def _remover_item(self):
        """Remove o item selecionado da lista e deleta o arquivo"""
        item = self.lst_notas.currentItem()
        if item:
            resposta = QMessageBox.question(
                self, 
                "Confirmar", 
                "Tem certeza que deseja remover este item permanentemente?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if resposta == QMessageBox.Yes:
                dados = item.data(Qt.UserRole)
                try:
                    Path(dados["path"]).unlink()
                    self.lst_notas.takeItem(self.lst_notas.row(item))
                    self.statusBar().showMessage("Item removido com sucesso", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Não foi possível remover:\n{str(e)}")
    
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
                
                # Adiciona à lista se não existir
                self._adicionar_item_lista(file_path, "xml")
                
            except Exception as e:
                self.statusBar().showMessage("Erro ao processar NFe", 3000)
                QMessageBox.critical(self, "Erro", f"Falha ao processar NFe:\n{str(e)}")
    
    def _adicionar_item_lista(self, path, tipo):
        """Adiciona um novo item à lista de notas"""
        nome_arquivo = Path(path).name
        
        if tipo == "xml":
            for i in range(self.lst_notas.count()):
                item = self.lst_notas.item(i)
                if item.data(Qt.UserRole)["path"] == path:
                    return  # Já existe
            
            item = QListWidgetItem(f"📄 {nome_arquivo}")
            item.setData(Qt.UserRole, {"tipo": "xml", "path": path})
            self.lst_notas.addItem(item)
    
    def abrir_nota(self, item):
        """Abre a nota selecionada na lista"""
        dados = item.data(Qt.UserRole)
        
        try:
            if dados["tipo"] == "xml":
                # Carrega XML original
                with open(dados["path"], 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                
                nota = self.xml_processor.parse_xml(xml_content)
                self.set_nota(nota)
                self.tabs.setCurrentIndex(0)  # Aba de cálculos
                
            elif dados["tipo"] == "calculo":
                # Carrega cálculo salvo
                with open(dados["path"], 'r', encoding='utf-8') as f:
                    dados_calculo = json.load(f)
                
                # Cria janela de visualização
                self.calculation_window = CalculationWindow()
                self.calculation_window.carregar_dados_salvos(dados_calculo["calculos"][-1])
                self.calculation_window.show()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir:\n{str(e)}")
    
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