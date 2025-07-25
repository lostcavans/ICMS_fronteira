from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFormLayout, 
                            QLineEdit, QPushButton, QGroupBox, QScrollArea,
                            QCheckBox, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, QDateTime
from core.models import NotaFiscal, Impostos, Produto, RegimeTributario
from core.calculator import ICMSCalculator
from core.nfe_parser import NotaFiscalParser
from core.config_manager import ConfigManager
import json
from pathlib import Path
import os

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
        
        self.btn_carregar = QPushButton("Carregar XML")
        self.btn_carregar.clicked.connect(self.carregar_xml)
        
        self.btn_calcular = QPushButton("Calcular")
        self.btn_calcular.clicked.connect(self.calcular)
        
        self.btn_salvar = QPushButton("Salvar Cálculo")
        self.btn_salvar.clicked.connect(self.salvar_calculo)
        
        self.btn_agrupar = QPushButton("Agrupar Produtos")
        self.btn_agrupar.setCheckable(True)
        self.btn_agrupar.clicked.connect(self.alternar_agrupamento)
        
        btn_layout.addWidget(self.btn_carregar)
        btn_layout.addWidget(self.btn_calcular)
        btn_layout.addWidget(self.btn_salvar)
        btn_layout.addWidget(self.btn_agrupar)
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
    
    def carregar_xml(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Nota Fiscal", "", "XML Files (*.xml)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    xml_content = file.read()
                
                nota = NotaFiscalParser.parse_xml(xml_content)
                self.set_nota(nota)
                QMessageBox.information(self, "Sucesso", "Nota fiscal carregada com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao carregar XML:\n{str(e)}")
    
    def set_nota(self, nota: NotaFiscal, agrupar: bool = False):
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
        self.lbl_vicmsst.setText(f"R$ 0,00")
        
        # Preenche alíquota interestadual
        self.txt_aliq_interestadual.setText(str(nota.aliquota_interestadual))
        
        # Preenche tabela de produtos
        self.table_produtos.setRowCount(len(nota.produtos))
        for row, produto in enumerate(nota.produtos):
            self.table_produtos.setItem(row, 0, QTableWidgetItem(produto.item))
            self.table_produtos.setItem(row, 1, QTableWidgetItem(produto.descricao))
            self.table_produtos.setItem(row, 2, QTableWidgetItem(produto.ncm))
            self.table_produtos.setItem(row, 3, QTableWidgetItem(produto.cest or ""))
            self.table_produtos.setItem(row, 4, QTableWidgetItem(f"R$ {produto.valor_total:,.2f}"))
            self.table_produtos.setItem(row, 5, QTableWidgetItem(f"R$ {produto.valor_icms:,.2f}"))
            self.table_produtos.setItem(row, 6, QTableWidgetItem("R$ 0,00"))
            self.table_produtos.setItem(row, 7, QTableWidgetItem("R$ 0,00"))
    
    def alternar_agrupamento(self):
        if self.current_nota:
            self.set_nota(self.current_nota, self.btn_agrupar.isChecked())
    
    def calcular(self):
        if not self.current_nota:
            QMessageBox.warning(self, "Aviso", "Nenhuma nota fiscal selecionada")
            return
            
        try:
            # Verifica campos obrigatórios
            campos_obrigatorios = [
                (self.txt_aliq_interestadual, "Alíquota Interestadual"),
                (self.txt_aliq_interna, "Alíquota Interna"),
                (self.txt_mva_original, "MVA Original"),
                (self.txt_mva_cnae, "MVA CNAE")
            ]
            
            for campo, nome in campos_obrigatorios:
                if not campo.text():
                    raise ValueError(f"O campo {nome} é obrigatório")
            
            impostos = Impostos(
                aliquota_interna=float(self.txt_aliq_interna.text()),
                aliquota_interestadual=float(self.txt_aliq_interestadual.text()),
                mva_original=float(self.txt_mva_original.text()),
                mva_cnae=float(self.txt_mva_cnae.text()),
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
            
            for row in range(self.table_produtos.rowCount()):
                # Recupera dados do produto
                item = self.table_produtos.item(row, 0)
                descricao = self.table_produtos.item(row, 1)
                ncm = self.table_produtos.item(row, 2)
                cest = self.table_produtos.item(row, 3)
                valor_text = self.table_produtos.item(row, 4).text()
                icms_text = self.table_produtos.item(row, 5).text()
                
                valor_total = float(valor_text.replace("R$", "").replace(".", "").replace(",", ".").strip())
                valor_icms = float(icms_text.replace("R$", "").replace(".", "").replace(",", ".").strip())
                
                # Cria objeto Produto temporário
                produto = Produto(
                    item=item.text(),
                    codigo="",
                    descricao=descricao.text(),
                    ncm=ncm.text(),
                    cest=cest.text() if cest else None,
                    cfop="",
                    unidade="",
                    quantidade=0,
                    valor_unitario=0,
                    valor_total=valor_total,
                    valor_ipi=self.current_nota.valor_ipi,
                    valor_icms=valor_icms,
                    valor_frete=self.current_nota.valor_frete,
                    valor_seguro=self.current_nota.valor_seguro,
                    valor_desconto=self.current_nota.valor_desconto
                )
                
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
                
                # ICMS Uso/Consumo (novo cálculo)
                uso_consumo = self.calculator.calcular_uso_consumo(produto, impostos)
                total_uso_consumo += uso_consumo
                
                # ICMS Redução
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
            QMessageBox.warning(self, "Aviso", "Nenhuma nota fiscal selecionada")
            return
            
        try:
            if self.lbl_icms_st.text() == "R$ 0,00":
                if QMessageBox.question(self, "Confirmação", 
                                      "Parece que o cálculo não foi realizado. Deseja salvar mesmo assim?",
                                      QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                    return
            
            # Coletar dados dos produtos
            produtos = []
            for row in range(self.table_produtos.rowCount()):
                item = self.table_produtos.item(row, 0)
                descricao = self.table_produtos.item(row, 1)
                ncm = self.table_produtos.item(row, 2)
                cest = self.table_produtos.item(row, 3)
                valor = self.table_produtos.item(row, 4)
                icms = self.table_produtos.item(row, 5)
                st = self.table_produtos.item(row, 6)
                tributado = self.table_produtos.item(row, 7)
                
                if None in [item, descricao, ncm, valor, icms, st, tributado]:
                    continue
                    
                produto = {
                    'item': item.text(),
                    'descricao': descricao.text(),
                    'ncm': ncm.text(),
                    'cest': cest.text() if cest else "",
                    'valor_total': float(valor.text().replace("R$", "").replace(".", "").replace(",", ".").strip()),
                    'valor_icms': float(icms.text().replace("R$", "").replace(".", "").replace(",", ".").strip()),
                    'icms_st': float(st.text().replace("R$", "").replace(".", "").replace(",", ".").strip()),
                    'icms_tributado': float(tributado.text().replace("R$", "").replace(".", "").replace(",", ".").strip())
                }
                produtos.append(produto)
            
            calculo = {
                "data": QDateTime.currentDateTime().toString(Qt.ISODate),
                "nota": self.current_nota.chave,
                "numero": self.current_nota.numero,
                "emitente": {
                    "nome": self.current_nota.emitente_nome,
                    "cnpj": self.current_nota.emitente_cnpj,
                    "uf": self.current_nota.emitente_uf
                },
                "destinatario": {
                    "nome": self.current_nota.destinatario_nome,
                    "uf": self.current_nota.destinatario_uf
                },
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
                },
                "produtos": produtos
            }
            
            # Salva em arquivo
            calculos_dir = Path("calculos")
            calculos_dir.mkdir(exist_ok=True)
            
            arquivo = calculos_dir / f"{self.current_nota.chave}.json"
            
            dados = {"calculos": []}
            if arquivo.exists():
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    if not isinstance(dados.get("calculos"), list):
                        dados["calculos"] = []
                except:
                    dados["calculos"] = []
            
            dados["calculos"].append(calculo)
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(self, "Sucesso", "Cálculo salvo com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar cálculo:\n{str(e)}")
    
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
    
    def carregar_dados_salvos(self, dados_calculo):
        """Carrega dados de um cálculo salvo anteriormente"""
        try:
            # Cria objeto NotaFiscal básico
            nota = NotaFiscal(
                chave=dados_calculo.get("nota", ""),
                numero=dados_calculo.get("numero", ""),
                emitente_nome=dados_calculo.get("emitente", {}).get("nome", ""),
                emitente_cnpj=dados_calculo.get("emitente", {}).get("cnpj", ""),
                emitente_uf=dados_calculo.get("emitente", {}).get("uf", ""),
                destinatario_nome=dados_calculo.get("destinatario", {}).get("nome", ""),
                destinatario_uf=dados_calculo.get("destinatario", {}).get("uf", ""),
                emitente_regime=RegimeTributario.NORMAL,
                produtos=[],
                valor_total=0,
                valor_frete=0,
                valor_seguro=0,
                valor_desconto=0,
                valor_ipi=0,
                valor_icms=0,
                aliquota_interestadual=0
            )
            
            self.set_nota(nota)
            
            # Preenche parâmetros
            params = dados_calculo.get("parametros", {})
            self.txt_aliq_interestadual.setText(str(params.get("aliq_interestadual", "")))
            self.txt_aliq_interna.setText(str(params.get("aliq_interna", "")))
            self.txt_mva_original.setText(str(params.get("mva_original", "")))
            self.txt_mva_cnae.setText(str(params.get("mva_cnae", "")))
            self.txt_difal.setText(str(params.get("difal", "")))
            self.txt_aliq_credito.setText(str(params.get("aliq_credito", "")))
            self.txt_aliq_reducao.setText(str(params.get("aliq_reducao", "")))
            self.chk_desconto.setChecked(params.get("considerar_desconto", True))
            self.chk_credito.setChecked(params.get("usar_credito_manual", False))
            
            # Preenche resultados
            results = dados_calculo.get("resultados", {})
            self.lbl_icms_st.setText(results.get("icms_st", "R$ 0,00"))
            self.lbl_icms_tributado.setText(results.get("icms_tributado", "R$ 0,00"))
            self.lbl_icms_uso_consumo.setText(results.get("icms_uso_consumo", "R$ 0,00"))
            self.lbl_icms_reducao.setText(results.get("icms_reducao", "R$ 0,00"))
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar cálculo:\n{str(e)}")