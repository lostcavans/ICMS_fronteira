from xml.etree import ElementTree as ET
from typing import Dict
from core.models import NotaFiscal, Produto, RegimeTributario

class NotaFiscalParser:
    @staticmethod
    def parse_xml(xml_content: str) -> NotaFiscal:
        namespace = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
        root = ET.fromstring(xml_content)
        
        inf_nfe = root.find('.//ns:NFe/ns:infNFe', namespace)
        ide = inf_nfe.find('ns:ide', namespace)
        emit = inf_nfe.find('ns:emit', namespace)
        dest = inf_nfe.find('ns:dest', namespace)
        total = inf_nfe.find('ns:total/ns:ICMSTot', namespace)
        
        # Converter CRT para RegimeTributario
        crt = emit.find('ns:CRT', namespace).text
        regime_map = {
            '1': RegimeTributario.SIMPLES,
            '2': RegimeTributario.SIMPLES_EXCEDENTE,
            '3': RegimeTributario.NORMAL
        }
        regime = regime_map.get(crt, RegimeTributario.NORMAL)
        
        # Parse produtos
        produtos = []
        for det in inf_nfe.findall('ns:det', namespace):
            prod = det.find('ns:prod', namespace)
            imposto = det.find('ns:imposto', namespace)
            icms = imposto.find('ns:ICMS/ns:ICMS00', namespace)
            
            produto = Produto(
                item=det.get('nItem'),
                codigo=prod.find('ns:cProd', namespace).text,
                descricao=prod.find('ns:xProd', namespace).text,
                ncm=prod.find('ns:NCM', namespace).text,
                cfop=prod.find('ns:CFOP', namespace).text,
                unidade=prod.find('ns:uCom', namespace).text,
                quantidade=float(prod.find('ns:qCom', namespace).text),
                valor_unitario=float(prod.find('ns:vUnCom', namespace).text),
                valor_total=float(prod.find('ns:vProd', namespace).text),
                valor_ipi=float(imposto.find('ns:IPI/ns:IPITrib/ns:vIPI', namespace).text),
                valor_icms=float(icms.find('ns:vICMS', namespace).text),
                valor_frete=float(prod.find('ns:vFrete', namespace).text) if prod.find('ns:vFrete', namespace) is not None else 0.0,
                valor_seguro=float(prod.find('ns:vSeg', namespace).text) if prod.find('ns:vSeg', namespace) is not None else 0.0,
                valor_desconto=0.0,
                aliquota_icms=float(icms.find('ns:pICMS', namespace).text)
            )
            produtos.append(produto)
        
        # Criar objeto NotaFiscal
        nota = NotaFiscal(
            chave=inf_nfe.get('Id').replace('NFe', ''),
            numero=ide.find('ns:nNF', namespace).text,
            emitente_cnpj=emit.find('ns:CNPJ', namespace).text,
            emitente_nome=emit.find('ns:xNome', namespace).text,
            destinatario_nome=dest.find('ns:xNome', namespace).text,
            emitente_regime=regime,
            emitente_uf=emit.find('ns:enderEmit/ns:UF', namespace).text,
            destinatario_uf=dest.find('ns:enderDest/ns:UF', namespace).text,
            produtos=produtos,
            valor_total=float(total.find('ns:vProd', namespace).text),
            valor_frete=float(total.find('ns:vFrete', namespace).text),
            valor_seguro=float(total.find('ns:vSeg', namespace).text),
            valor_desconto=float(total.find('ns:vDesc', namespace).text),
            valor_ipi=float(total.find('ns:vIPI', namespace).text),
            valor_icms=float(total.find('ns:vICMS', namespace).text),
            aliquota_interestadual=float(produtos[0].aliquota_icms) if produtos else 0.0
        )
        
        return nota