# calculation_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout, 
                            QLineEdit, QPushButton, QGroupBox, QScrollArea,
                            QCheckBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QDateTime
from core.models import NotaFiscal, Impostos
from core.calculator import ICMSCalculator
from core.config_manager import ConfigManager
import json
from pathlib import Path

class CalculationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_nota = None
        self.calculator = ICMSCalculator()
        self.config = ConfigManager()
        self._setup_ui()
    
    def _setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.scroll_layout = QVBoxLayout(content)
        
        # Grupo de informações da nota
        self.info_group = QGroupBox("Informações da Nota")
        self.info_layout = QFormLayout()
        
        self.lbl_chave = QLabel()
        self.lbl_numero = QLabel()
        self.lbl_emitente = QLabel()
        self.lbl_destinatario = QLabel()
        self.lbl_uf_origem = QLabel()
        self.lbl_uf_destino = QLabel()
        self.lbl_valor_total = QLabel()
        self.lbl_crt = QLabel()
        
        self.info_layout.addRow("Chave:", self.lbl_chave)
        self.info_layout.addRow("Número:", self.lbl_numero)
        self.info_layout.addRow("Emitente:", self.lbl_emitente)
        self.info_layout.addRow("Destinatário:", self.lbl_destinatario)
        self.info_layout.addRow("UF Origem:", self.lbl_uf_origem)
        self.info_layout.addRow("UF Destino:", self.lbl_uf_destino)
        self.info_layout.addRow("Valor Total:", self.lbl_valor_total)
        self.info_layout.addRow("Regime Tributário:", self.lbl_crt)
        
        self.info_group.setLayout(self.info_layout)
        self.scroll_layout.addWidget(self.info_group)
        
        # Grupo de valores da nota
        self.valores_group = QGroupBox("Valores da Nota")
        self.valores_layout = QFormLayout()
        
        self.lbl_vprod = QLabel()
        self.lbl_vipi = QLabel()
        self.lbl_vfrete = QLabel()
        self.lbl_vseg = QLabel()
        self.lbl_vdesc = QLabel()
        self.lbl_vicms = QLabel()
        self.lbl_vicmsst = QLabel()
        
        self.valores_layout.addRow("Valor Produtos:", self.lbl_vprod)
        self.valores_layout.addRow("Valor IPI:", self.lbl_vipi)
        self.valores_layout.addRow("Valor Frete:", self.lbl_vfrete)
        self.valores_layout.addRow("Valor Seguro:", self.lbl_vseg)
        self.valores_layout.addRow("Valor Desconto:", self.lbl_vdesc)
        self.valores_layout.addRow("Valor ICMS:", self.lbl_vicms)
        self.valores_layout.addRow("Valor ICMS ST:", self.lbl_vicmsst)
        
        self.valores_group.setLayout(self.valores_layout)
        self.scroll_layout.addWidget(self.valores_group)
        
        # Grupo de parâmetros
        self.params_group = QGroupBox("Parâmetros de Cálculo")
        self.params_layout = QFormLayout()
        
        self.txt_aliq_interestadual = QLineEdit()
        self.txt_aliq_interna = QLineEdit()
        self.txt_mva_original = QLineEdit()
        self.txt_mva_cnae = QLineEdit()
        self.txt_difal = QLineEdit()
        self.txt_aliq_credito = QLineEdit()
        self.txt_aliq_reducao = QLineEdit()
        
        self.chk_desconto = QCheckBox("Considerar desconto?")
        self.chk_desconto.setChecked(True)
        
        self.chk_credito = QCheckBox("Usar crédito manual?")
        self.chk_credito.setChecked(False)
        
        self.params_layout.addRow("Alíquota Interestadual (%):", self.txt_aliq_interestadual)
        self.params_layout.addRow("Alíquota Interna (%):", self.txt_aliq_interna)
        self.params_layout.addRow("MVA Original (%):", self.txt_mva_original)
        self.params_layout.addRow("MVA CNAE (%):", self.txt_mva_cnae)
        self.params_layout.addRow("DIFAL (%):", self.txt_difal)
        self.params_layout.addRow("Alíquota Crédito (%):", self.txt_aliq_credito)
        self.params_layout.addRow("Alíquota Redução (%):", self.txt_aliq_reducao)
        self.params_layout.addRow(self.chk_desconto)
        self.params_layout.addRow(self.chk_credito)
        
        self.params_group.setLayout(self.params_layout)
        self.scroll_layout.addWidget(self.params_group)
        
        # Botões de ação
        btn_layout = QVBoxLayout()
        
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.clicked.connect(self.calcular)
        
        self.btn_salvar = QPushButton("Salvar Cálculo")
        self.btn_salvar.clicked.connect(self.salvar_calculo)
        
        btn_layout.addWidget(self.btn_calcular)
        btn_layout.addWidget(self.btn_salvar)
        self.scroll_layout.addLayout(btn_layout)
        
        # Resultados
        self.result_group = QGroupBox("Resultados")
        self.result_layout = QFormLayout()
        
        self.lbl_icms_st = QLabel("R$ 0,00")
        self.lbl_icms_tributado = QLabel("R$ 0,00")
        self.lbl_icms_uso_consumo = QLabel("R$ 0,00")
        self.lbl_icms_reducao = QLabel("R$ 0,00")
        
        self.result_layout.addRow("ICMS ST:", self.lbl_icms_st)
        self.result_layout.addRow("ICMS Tributado:", self.lbl_icms_tributado)
        self.result_layout.addRow("ICMS Uso/Consumo:", self.lbl_icms_uso_consumo)
        self.result_layout.addRow("ICMS Redução:", self.lbl_icms_reducao)
        
        self.result_group.setLayout(self.result_layout)
        self.scroll_layout.addWidget(self.result_group)
        
        # Tabela de produtos
        self.table_produtos = QTableWidget()
        self.table_produtos.setColumnCount(8)
        self.table_produtos.setHorizontalHeaderLabels([
            "Item", "Descrição", "NCM", "CEST", "Valor", 
            "ICMS", "ST", "Tributado"
        ])
        self.table_produtos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scroll_layout.addWidget(self.table_produtos)
        
        scroll.setWidget(content)
        self.layout.addWidget(scroll)
    
    def set_nota(self, nota: NotaFiscal):
        self.current_nota = nota
        
        # Preenche informações básicas
        self.lbl_chave.setText(nota.chave)
        self.lbl_numero.setText(nota.numero)
        self.lbl_emitente.setText(f"{nota.emitente_nome} ({nota.emitente_cnpj})")
        self.lbl_destinatario.setText(f"{nota.destinatario_nome} ({nota.destinatario_uf})")
        self.lbl_uf_origem.setText(nota.emitente_uf)
        self.lbl_uf_destino.setText(nota.destinatario_uf)
        self.lbl_valor_total.setText(f"R$ {nota.valor_total:,.2f}")
        self.lbl_crt.setText(str(nota.emitente_regime))
        
        # Preenche valores
        self.lbl_vprod.setText(f"R$ {nota.valor_total:,.2f}")
        self.lbl_vipi.setText(f"R$ {nota.valor_ipi:,.2f}")
        self.lbl_vfrete.setText(f"R$ {nota.valor_frete:,.2f}")
        self.lbl_vseg.setText(f"R$ {nota.valor_seguro:,.2f}")
        self.lbl_vdesc.setText(f"R$ {nota.valor_desconto:,.2f}")
        self.lbl_vicms.setText(f"R$ {nota.valor_icms:,.2f}")
        self.lbl_vicmsst.setText(f"R$ 0,00")  # Será calculado
        
        # Preenche parâmetros padrão
        self.txt_aliq_interestadual.setText(str(nota.aliquota_interestadual))
        self.txt_aliq_interna.setText(str(self.config.get_aliquota_interestadual(nota.destinatario_uf) or "20.5"))
        
        # Preenche tabela de produtos
        self.table_produtos.setRowCount(len(nota.produtos))
        for row, produto in enumerate(nota.produtos):
            self.table_produtos.setItem(row, 0, QTableWidgetItem(produto.item))
            self.table_produtos.setItem(row, 1, QTableWidgetItem(produto.descricao))
            self.table_produtos.setItem(row, 2, QTableWidgetItem(produto.ncm))
            self.table_produtos.setItem(row, 3, QTableWidgetItem(produto.cest))
            self.table_produtos.setItem(row, 4, QTableWidgetItem(f"R$ {produto.valor_total:,.2f}"))
            self.table_produtos.setItem(row, 5, QTableWidgetItem(f"R$ {produto.valor_icms:,.2f}"))
            self.table_produtos.setItem(row, 6, QTableWidgetItem("R$ 0,00"))  # ST
            self.table_produtos.setItem(row, 7, QTableWidgetItem("R$ 0,00"))  # Tributado
    
    def calcular(self):
        if not self.current_nota:
            return
            
        try:
            impostos = Impostos(
                aliquota_interna=float(self.txt_aliq_interna.text()),
                aliquota_interestadual=float(self.txt_aliq_interestadual.text()),
                mva_original=float(self.txt_mva_original.text()) if self.txt_mva_original.text() else None,
                mva_cnae=float(self.txt_mva_cnae.text()) if self.txt_mva_cnae.text() else None,
                difal=float(self.txt_difal.text()) if self.txt_difal.text() else None,
                aliquota_credito=float(self.txt_aliq_credito.text()) if self.txt_aliq_credito.text() else None,
                aliquota_reducao=float(self.txt_aliq_reducao.text()) if self.txt_aliq_reducao.text() else None
            )
            
            total_st = 0.0
            total_tributado = 0.0
            total_uso_consumo = 0.0
            total_reducao = 0.0
            
            considerar_desconto = self.chk_desconto.isChecked()
            usar_credito_manual = self.chk_credito.isChecked()
            
            for row, produto in enumerate(self.current_nota.produtos):
                # ICMS ST
                st = self.calculator.calcular_icms_st(
                    produto, impostos, 
                    self.current_nota.emitente_regime,
                    considerar_desconto
                )
                self.table_produtos.item(row, 6).setText(f"R$ {st:,.2f}")
                total_st += st
                
                # ICMS Tributado
                tributado = self.calculator.calcular_icms_tributado(
                    produto, impostos,
                    self.current_nota.emitente_regime,
                    usar_credito_manual
                )
                self.table_produtos.item(row, 7).setText(f"R$ {tributado:,.2f}")
                total_tributado += tributado
                
                # ICMS Uso/Consumo (simplificado)
                uso_consumo = st * 0.5 if self.current_nota.destinatario_uf == 'PE' else 0
                total_uso_consumo += uso_consumo
                
                # ICMS Redução (simplificado)
                reducao = tributado * 0.3 if impostos.aliquota_reducao else 0
                total_reducao += reducao
            
            # Atualiza totais
            self.lbl_icms_st.setText(f"R$ {total_st:,.2f}")
            self.lbl_icms_tributado.setText(f"R$ {total_tributado:,.2f}")
            self.lbl_icms_uso_consumo.setText(f"R$ {total_uso_consumo:,.2f}")
            self.lbl_icms_reducao.setText(f"R$ {total_reducao:,.2f}")
            
        except ValueError as e:
            QMessageBox.warning(self, "Erro", f"Valor inválido inserido: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha no cálculo: {str(e)}")
    
    def salvar_calculo(self):
        if not self.current_nota:
            return
            
        calculo = {
            "data": QDateTime.currentDateTime().toString(Qt.ISODate),
            "nota": self.current_nota.chave,
            "parametros": {
                "aliq_interestadual": self.txt_aliq_interestadual.text(),
                "aliq_interna": self.txt_aliq_interna.text(),
                "mva_original": self.txt_mva_original.text(),
                "mva_cnae": self.txt_mva_cnae.text(),
                "difal": self.txt_difal.text(),
                "aliq_credito": self.txt_aliq_credito.text(),
                "aliq_reducao": self.txt_aliq_reducao.text(),
                "considerar_desconto": self.chk_desconto.isChecked(),
                "usar_credito_manual": self.chk_credito.isChecked()
            },
            "resultados": {
                "icms_st": self.lbl_icms_st.text(),
                "icms_tributado": self.lbl_icms_tributado.text(),
                "icms_uso_consumo": self.lbl_icms_uso_consumo.text(),
                "icms_reducao": self.lbl_icms_reducao.text()
            }
        }
        
        # Salva em JSON
        calculos_dir = Path("calculos")
        calculos_dir.mkdir(exist_ok=True)
        
        arquivo = calculos_dir / f"{self.current_nota.chave}.json"
        
        try:
            if arquivo.exists():
                with open(arquivo, 'r') as f:
                    dados = json.load(f)
            else:
                dados = {"calculos": []}
            
            dados["calculos"].append(calculo)
            
            with open(arquivo, 'w') as f:
                json.dump(dados, f, indent=2)
            
            QMessageBox.information(self, "Sucesso", "Cálculo salvo com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar cálculo: {str(e)}")
    
    def limpar_dados(self):
        self.current_nota = None
        self.table_produtos.setRowCount(0)
        
        # Limpa labels
        for label in [self.lbl_chave, self.lbl_numero, self.lbl_emitente,
                     self.lbl_destinatario, self.lbl_uf_origem, self.lbl_uf_destino,
                     self.lbl_valor_total, self.lbl_crt, self.lbl_vprod, self.lbl_vipi,
                     self.lbl_vfrete, self.lbl_vseg, self.lbl_vdesc, self.lbl_vicms,
                     self.lbl_vicmsst, self.lbl_icms_st, self.lbl_icms_tributado,
                     self.lbl_icms_uso_consumo, self.lbl_icms_reducao]:
            label.clear()
        
        # Limpa campos editáveis
        for field in [self.txt_aliq_interestadual, self.txt_aliq_interna,
                     self.txt_mva_original, self.txt_mva_cnae, self.txt_difal,
                     self.txt_aliq_credito, self.txt_aliq_reducao]:
            field.clear()
        
        self.chk_desconto.setChecked(True)
        self.chk_credito.setChecked(False)