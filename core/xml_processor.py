from lxml import etree
from typing import List, Optional
from core.models import NotaFiscal, Produto, RegimeTributario

class XMLProcessor:
    NS = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    
    def parse_xml(self, xml_content: str) -> Optional[NotaFiscal]:
        try:
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            if not self._is_valid_nfe(root):
                raise ValueError("Arquivo XML não é uma NFe válida")
            
            return self._parse_nfe(root)
        except Exception as e:
            raise ValueError(f"Falha ao processar XML: {str(e)}")

    def _is_valid_nfe(self, root) -> bool:
        """Verifica se o XML tem a estrutura básica de uma NFe"""
        return (root.tag == '{http://www.portalfiscal.inf.br/nfe}nfeProc' or 
                root.tag == '{http://www.portalfiscal.inf.br/nfe}NFe')

    def _parse_nfe(self, root) -> NotaFiscal:
        # Correção para o warning de FutureWarning
        inf_nfe = root.find('.//nfe:infNFe', self.NS)
        if inf_nfe is None:
            inf_nfe = root.find('.//infNFe')
        if inf_nfe is None:
            raise ValueError("Elemento infNFe não encontrado no XML")
        
        ide = self._safe_find(inf_nfe, 'nfe:ide', self.NS)
        emit = self._safe_find(inf_nfe, 'nfe:emit', self.NS)
        dest = self._safe_find(inf_nfe, 'nfe:dest', self.NS)
        total = self._safe_find(inf_nfe, 'nfe:total/nfe:ICMSTot', self.NS)
        
        # Extrai nome do destinatário se existir
        destinatario_nome = self._safe_text(dest, 'nfe:xNome', self.NS)
        
        emitente_uf = self._safe_text(emit, 'nfe:enderEmit/nfe:UF', self.NS)
        destinatario_uf = self._safe_text(dest, 'nfe:enderDest/nfe:UF', self.NS)
        
        crt = self._safe_text(emit, 'nfe:CRT', self.NS, '3')
        regime = self._parse_regime_tributario(crt)
        
        produtos = self._parse_produtos(inf_nfe)
        aliquota_interestadual = self._get_aliquota_interestadual(inf_nfe)
        
        return NotaFiscal(
            chave=inf_nfe.get('Id', '')[-44:],
            numero=self._safe_text(ide, 'nfe:nNF', self.NS),
            emitente_cnpj=self._safe_text(emit, 'nfe:CNPJ', self.NS),
            emitente_nome=self._safe_text(emit, 'nfe:xNome', self.NS),
            destinatario_nome=destinatario_nome,
            emitente_regime=regime,
            emitente_uf=emitente_uf,
            destinatario_uf=destinatario_uf,
            produtos=produtos,
            valor_total=self._safe_float(total, 'nfe:vNF', self.NS),
            valor_frete=self._safe_float(total, 'nfe:vFrete', self.NS),
            valor_seguro=self._safe_float(total, 'nfe:vSeg', self.NS),
            valor_desconto=self._safe_float(total, 'nfe:vDesc', self.NS),
            valor_ipi=self._safe_float(total, 'nfe:vIPI', self.NS),
            valor_icms=self._safe_float(total, 'nfe:vICMS', self.NS),
            aliquota_interestadual=aliquota_interestadual
        )

    def _parse_produtos(self, inf_nfe) -> List[Produto]:
        produtos = []
        for det in inf_nfe.findall('.//nfe:det', self.NS):
            prod = self._safe_find(det, 'nfe:prod', self.NS)
            imposto = self._safe_find(det, 'nfe:imposto', self.NS)
            
            # Extrai valores de frete e seguro se existirem
            valor_frete = self._safe_float(det, 'nfe:prod/nfe:vFrete', self.NS)
            valor_seguro = self._safe_float(det, 'nfe:prod/nfe:vSeg', self.NS)
            
            produtos.append(Produto(
                item=det.get('nItem', ''),
                codigo=self._safe_text(prod, 'nfe:cProd', self.NS),
                descricao=self._safe_text(prod, 'nfe:xProd', self.NS),
                ncm=self._safe_text(prod, 'nfe:NCM', self.NS),
                cest=self._safe_text(prod, 'nfe:CEST', self.NS),
                cfop=self._safe_text(prod, 'nfe:CFOP', self.NS),
                unidade=self._safe_text(prod, 'nfe:uCom', self.NS),
                quantidade=self._safe_float(prod, 'nfe:qCom', self.NS),
                valor_unitario=self._safe_float(prod, 'nfe:vUnCom', self.NS),
                valor_total=self._safe_float(prod, 'nfe:vProd', self.NS),
                valor_ipi=self._safe_float(imposto, 'nfe:IPI/nfe:IPITrib/nfe:vIPI', self.NS),
                valor_icms=self._safe_float(imposto, 'nfe:ICMS//nfe:vICMS', self.NS),
                valor_frete=valor_frete,
                valor_seguro=valor_seguro
            ))
        return produtos

    def _get_aliquota_interestadual(self, inf_nfe) -> float:
        for det in inf_nfe.findall('.//nfe:det', self.NS):
            imposto = self._safe_find(det, 'nfe:imposto', self.NS)
            if imposto is not None:
                p_icms = imposto.find('.//nfe:pICMS', self.NS)
                if p_icms is not None and p_icms.text:
                    try:
                        return float(p_icms.text)
                    except ValueError:
                        continue
        return 0.0

    def _parse_regime_tributario(self, crt: str) -> RegimeTributario:
        crt = crt.strip() if crt else '3'
        return {
            '1': RegimeTributario.SIMPLES,
            '2': RegimeTributario.SIMPLES_EXCEDENTE,
            '3': RegimeTributario.NORMAL
        }.get(crt, RegimeTributario.NORMAL)

    def _safe_find(self, element, path, ns=None):
        return element.find(path, ns) if element is not None else None

    def _safe_text(self, element, path, ns=None, default=''):
        found = self._safe_find(element, path, ns)
        return found.text if found is not None else default

    def _safe_float(self, element, path, ns=None, default=0.0):
        try:
            return float(self._safe_text(element, path, ns, str(default)))
        except ValueError:
            return default
        
        # Adicionar em xml_processor.py
    def _validate_xml(self, xml_content: str) -> bool:
        from lxml import etree
        try:
            schema = etree.XMLSchema(file="nfe_schema.xsd")
            parser = etree.XMLParser(schema=schema)
            etree.fromstring(xml_content, parser)
            return True
        except etree.XMLSyntaxError as e:
            raise ValueError(f"XML inválido: {str(e)}")