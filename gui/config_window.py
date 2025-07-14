# config_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                            QPushButton, QComboBox, QMessageBox, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import json
from pathlib import Path

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.carregar_config()
    
    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Grupo de configurações gerais
        self.grp_geral = QGroupBox("Configurações Gerais")
        self.lyt_geral = QFormLayout()
        
        self.cmb_empresa = QComboBox()
        self.cmb_empresa.currentIndexChanged.connect(self.carregar_config_empresa)
        
        self.txt_aliq_interna = QLineEdit()
        self.txt_considerar_desconto = QCheckBox("Considerar desconto por padrão")
        self.txt_usar_credito_manual = QCheckBox("Usar crédito manual por padrão")
        
        self.lyt_geral.addRow("Empresa Padrão:", self.cmb_empresa)
        self.lyt_geral.addRow("Alíquota Interna Padrão (%):", self.txt_aliq_interna)
        self.lyt_geral.addRow(self.txt_considerar_desconto)
        self.lyt_geral.addRow(self.txt_usar_credito_manual)
        
        self.grp_geral.setLayout(self.lyt_geral)
        self.layout.addWidget(self.grp_geral)
        
        # Grupo de alíquotas por UF
        self.grp_aliquotas = QGroupBox("Alíquotas por UF")
        self.lyt_aliquotas = QFormLayout()
        
        self.uf_fields = {}
        ufs = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", 
               "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
               "RN", "RJ", "RO", "RR", "SC", "SP", "SE", "TO"]
        
        for uf in ufs:
            self.uf_fields[uf] = QLineEdit()
            self.lyt_aliquotas.addRow(f"{uf}:", self.uf_fields[uf])
        
        self.grp_aliquotas.setLayout(self.lyt_aliquotas)
        self.layout.addWidget(self.grp_aliquotas)
        
        # Botões de ação
        self.btn_salvar = QPushButton(QIcon(":/icons/save.png"), " Salvar Configurações")
        self.btn_salvar.clicked.connect(self.salvar_config)
        
        self.layout.addWidget(self.btn_salvar)
    
    def carregar_config(self):
        try:
            # Carrega empresas
            empresas_dir = Path("Z:/Fiscal/Simples Nacional/")
            if empresas_dir.exists():
                empresas = [d.name for d in empresas_dir.iterdir() if d.is_dir()]
                self.cmb_empresa.addItems(empresas)
            
            # Carrega configurações gerais
            config_path = Path("config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self.txt_aliq_interna.setText(str(config.get("aliq_interna_default", 20.5)))
                self.txt_considerar_desconto.setChecked(config.get("considerar_desconto", True))
                self.txt_usar_credito_manual.setChecked(config.get("usar_credito_manual", False))
                
                if config.get("empresa_padrao") and config["empresa_padrao"] in empresas:
                    self.cmb_empresa.setCurrentText(config["empresa_padrao"])
            
            # Carrega alíquotas por UF
            aliquotas_path = Path("aliquotas.json")
            if aliquotas_path.exists():
                with open(aliquotas_path, 'r') as f:
                    aliquotas = json.load(f)
                
                for uf, value in aliquotas.items():
                    if uf in self.uf_fields:
                        self.uf_fields[uf].setText(str(value))
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar configurações:\n{str(e)}")
    
    def carregar_config_empresa(self):
        empresa = self.cmb_empresa.currentText()
        if not empresa:
            return
            
        try:
            config_path = Path(f"empresas/{empresa}.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self.txt_aliq_interna.setText(str(config.get("aliq_interna", 20.5)))
                self.txt_considerar_desconto.setChecked(config.get("considerar_desconto", True))
                self.txt_usar_credito_manual.setChecked(config.get("usar_credito_manual", False))
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar configurações da empresa:\n{str(e)}")
    
    def salvar_config(self):
        try:
            # Salva configurações gerais
            config = {
                "empresa_padrao": self.cmb_empresa.currentText(),
                "aliq_interna_default": float(self.txt_aliq_interna.text()),
                "considerar_desconto": self.txt_considerar_desconto.isChecked(),
                "usar_credito_manual": self.txt_usar_credito_manual.isChecked()
            }
            
            with open("config.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            # Salva alíquotas por UF
            aliquotas = {uf: float(field.text()) for uf, field in self.uf_fields.items() if field.text()}
            
            with open("aliquotas.json", 'w') as f:
                json.dump(aliquotas, f, indent=2)
            
            # Salva configurações da empresa
            empresa = self.cmb_empresa.currentText()
            if empresa:
                empresa_config = {
                    "aliq_interna": float(self.txt_aliq_interna.text()),
                    "considerar_desconto": self.txt_considerar_desconto.isChecked(),
                    "usar_credito_manual": self.txt_usar_credito_manual.isChecked()
                }
                
                Path("empresas").mkdir(exist_ok=True)
                with open(f"empresas/{empresa}.json", 'w') as f:
                    json.dump(empresa_config, f, indent=2)
            
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
        
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Por favor, insira valores numéricos válidos para as alíquotas")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar configurações:\n{str(e)}")