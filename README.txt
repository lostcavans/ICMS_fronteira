    icms_fronteira/
    │
    ├── main.py                         # Ponto de entrada principal
    ├── core/
    │   ├── xml_processor.py            # Processamento de XMLs
    │   ├── calculator.py               # Cálculos de ICMS
    │   ├── cesta_basica.py             # Cálculos específicos para cesta básica
    │   ├── models.py                   # Modelos de dados
    │   └── utils.py                    # Utilitários
    ├── data/
    │   ├── config.json                 # Configurações do sistema
    │   ├── aliquotas.json              # Tabela de alíquotas interestaduais
    │   └── pauta_cesta_basica.json     # Valores de pauta para cesta básica
    ├── gui/
    │   ├── main_window.py              # Janela principal
    │   ├── calculation_window.py       # Janela de cálculos
    │   └── cesta_basica_window.py      # Janela de cesta básica
    ├── storage/
    │   ├── database.py                 # Gerenciamento do banco de dados
    │   └── history_manager.py          # Gerenciamento do histórico
    └── reports/
        └── pdf_generator.py            # Gerador de relatórios PDF



        Tenho um sistema de ICMs_fronteira que se deve ingresar esse arquivo que te passei, o pessoal da empresa me pediu as seguintes coisas que vou te pasar o que precisamos?

    valor do produto - nfe
    valor do frete - nfe
    valor do ipi - nfe
    valor da gnre - nfe
    valor do desconto - nfe
    aliquota interestadual - nfe/tabela aliquota interestadual
    aliquota interna - fixo/input
    fornecedor(simples ou regime normal) - nfe
    mva cnae - input
    mva original - input
    difal - input
    aliquota crédito - input
    aliquota de redução - input






    mva ajustada:
    ((1-aliquota interestadual)/(1-aliquota interna)(1+mva original))-1


    valor produto com desconto:
    v.base = v.prod - desconto


    icms destacado: 
    Definição da Base de Cálculo:

        Se o desconto não for considerado: Base de Cálculo = Valor do Produto (v.prod)
        Se o desconto for considerado: Base de Cálculo = Valor do Produto (v.prod) - Valor do Desconto (v.desconto)

    Cálculo do ICMS Destacado (aplicando benefícios fiscais em ordem de prioridade):

        Cenário 1: Há Alíquota de Redução?
            Se aliquotaReducao for maior que 0:
                ICMS Destacado = Base de Cálculo * aliquotaReducao * aliquotaInterestadual
        Cenário 2: Não há Alíquota de Redução, mas há Crédito de ICMS?
            Se creditoICMS for maior que 0 (e aliquotaReducao for 0 ou menor):
                ICMS Destacado = Base de Cálculo * creditoICMS
        Cenário 3: Não há Alíquota de Redução nem Crédito de ICMS (Cálculo Padrão)?
            (Se aliquotaReducao for 0 ou menor, e creditoICMS for 0 ou menor):
                ICMS Destacado = Base de Cálculo * aliquotaInterestadual


    icms st:
    (base de calculo st * aliquota interna)


    base de calculo tributada:
    se for normal = (v.prod + v.ipi + v.frete - icms destacado) / (1 - ali.interna)
    se não tiver crédito destacado na nota = v.prod + v.ipi + v.frete) / (1 - ali.interna)


    base de calculo st:
    se o fornecedor for do regime normal = (v.prod + v.ipi + v.frete) * (1 + mva ajustada)
    se o fornecedor for do regime simples = (v.prod + v.ipi + v.frete) * (1 + mva original)


    icms a recolher:
    tributado = (aliquota interna - aliquota interestadual) * base de calculo tributada
    tributada com difal do art. 363-A do decreto 44.650 = (difal * base de calculo tributada)
    tributado regime normal = (base de calculo tributada * mva cnae * ali.interna) - icms destacado
    st = (icms st - icms destacado) - gnre
    calculo com redução agrícola = (base de calculo tributada * mva cnae * 5,6%) - icms destacado
    calculo com redução industrial = (base de calculo tributada * mva cnae * 8,8%) - icms destacadoBom dia! Fiz esse resumo que eu creio que tenha tudo sobre os calculos, o que precisamos e os calculos necessários, se voce souber uma forma melhor de arrumar os calculos fique a vontade para mudar, mas as logicas são essas num resumo. Espero que ajude Alíquotas de ICMS para o estado de PERNAMBUCO (PE):

        De Acre (AC) para PE = 12%

        De Alagoas (AL) para PE = 12%

        De Amazonas (AM) para PE = 12%

        De Amapá (AP) para PE = 12%

        De Bahia (BA) para PE = 12%

        De Ceará (CE) para PE = 12%

        De Distrito Federal (DF) para PE = 12%

        De Espírito Santo (ES) para PE = 12%

        De Goiás (GO) para PE = 12%

        De Maranhão (MA) para PE = 12%

        De Mato Grosso (MT) para PE = 12%

        De Mato Grosso do Sul (MS) para PE = 12%

        De Minas Gerais (MG) para PE = 7%

        De Pará (PA) para PE = 12%

        De Paraíba (PB) para PE = 12%

        De Paraná (PR) para PE = 7%

        De Pernambuco (PE) para PE = 20.5%

        De Piauí (PI) para PE = 12%

        De Rio Grande do Norte (RN) para PE = 12%

        De Rio de Janeiro (RJ) para PE = 7%

        De Rondônia (RO) para PE = 12%

        De Roraima (RR) para PE = 12%

        De Santa Catarina (SC) para PE = 7%

        De São Paulo (SP) para PE = 7%

        De Sergipe (SE) para PE = 12%

        De Tocantins (TO) para PE = 12%   eu separei essa lista também que a gente pode usar para definir a aliquota interestadual de forma automatica, exemplo:  se o fornecedor for de são paulo, então automaticamente a aliquota fica ajustada para 7%, e por ai vai. De: Averton Souza

    Como nos podemos automatizar totalmente o fronteira?

    Podemos inicialmente ficar alimentando nossos banco de dados para termos dados suficientes para nos tentarmos ensinar uma IA caso seja viável.

    Podemos pegar as empresas que sempre são os mesmos produtos sempre para poder automatizar o processo repetitivo que nos faz gastar tempo, e tempo é precioso certo? kkkk

    Podemos começar automatizando uma empresa, no caso seria uma loja que sempre compra roupas de fora do estado, nos podemos automatizar essa empresa ja que sabemos sempre quais os produtos que ela compra, e conferimos ao final para saber se está correto (pelo menos por enquanto que está em periodo de teste).

    Um dos problemas de automatizar o fronteira das empresas que possuem produtos com ST, é justamente o mva original, que nos não conseguimos pegar facilmente e normalmente muda muito. Depender dos fornecedores, do ncm ou da descrição, é dificil confiar totalmente pois sempre tem algo que vai estar errado. Um produto que pode estar como um parafuso e um ncm de uma furadeira ou coisas desse tipo podem sempre acontecer por causa dos fornecedores, unica forma que vejo para burlar isso seria criar uma IA capaz de diferenciar o que é o que. Mas eu sinceramente não faço ideia de como mexer com IA.

    Essas são minhas ideias para automatizar totalmente os fronteiras, caso voce consiga pensar em algo mais pode falar que a gente desenrola junto.De: Averton Souza

    Outra função que podemos adicionar ao sistema seria incluir a parte de danilo a uma aba diferente, com funções mais voltadas para o departamento contabil, assim como temos nossa aba fiscal que é direcionada ao departamento contabil que ate agora temos apenas a funçao de fazer o fronteira, nos podiamos ter uma aba de empresas para cada departamento, com apenas as empresas que certo departamento presta serviços, pois possuem empresas que nos do fiscal fazemos que o departamento pessoal não faz por exemplo. Enfim acho que voce entendeu minha ideia. Com o tempo nos vamos adicionando essas coisas aos poucos e enquanto isso eu vou vendo e desenvolvendo outros tipos de abas que cada departamento pode ter, ou melhorar alguma coisa do que ja está pronto.De: Luis Miguel

    valor do produto - vProd (R$)
    valor do frete - vFrete (R$)
    valor do ipi - vIPI (R$)
    valor da gnre - vICMSST (R$)
    valor do desconto - vDesc (R$)
    valor do seguro - vSeg (R$)
    valor do crédito icms - vICMS (R$)
    aliquota interestadual - pICMS/input (%)
    aliquota interna - fixo(20,5%)/input (%)
    fornecedor(simples ou regime normal) - CRT (se 1 = simples nacional, se 2 = simples nacional com excedencia de receita e se 3 = regime normal)
    mva cnae - input (%)
    mva original - input (%)
    difal - input (%)
    aliquota crédito - input (%)
    aliquota de redução - input (%)

    crie um botão de escolha para considerar o desconto ou não.

    se considerar o desconto:
    v.prod = valor do produto - desconto
    se não:
    v.prod = valor do produto


    crie um botão para escolher se usa o icms crédito manual ou destacado.

    crédito icms:
    Cálculo do ICMS Destacado manual (aplicando benefícios fiscais em ordem de prioridade):

        Cenário 1: Há Alíquota de Redução?
            Se aliquotaReducao for maior que 0:
                ICMS crédito = Base de Cálculo * aliquotaReducao * aliquotaInterestadual
        Cenário 2: Não há Alíquota de Redução, mas há Crédito de ICMS?
            Se creditoICMS for maior que 0 (e aliquotaReducao for 0 ou menor):
                ICMS crédito = Base de Cálculo * creditoICMS
        Cenário 3: Não há Alíquota de Redução nem Crédito de ICMS (Cálculo Padrão)?
            (Se aliquotaReducao for 0 ou menor, e creditoICMS for 0 ou menor):
                ICMS crédito = Base de Cálculo * aliquotaInterestadual

    calculo do icms destacado na nota:
        so usar o valor que tem na tag de icms destacado.


    mva ajustada:
    ((1-aliquota interestadual)/(1-aliquota interna)(1+mva original))-1

    icms st:
    se o fornecedor for do regime normal = ((v.prod + v.ipi + v.frete + v.seguro) * (1 + mva ajustada) * (aliq. interna) - crédito icms) - GNRE
    se o fornecedor for do regime simples = ((v.prod + v.ipi + v.frete + v.seguro) * (1 + mva original) * (aliq. interna) - crédito icms) - GNRE

    icms tributado simples: 
    se a empresa for do simples e tiver regular = ((v.prod + v.ipi + v.frete + v.seguro) - icms crédito) / (1-aliq. interna) * (difal simples)
    se a empresa for do simples e não tiver regular = ((v.prod + v.ipi + v.frete + v.seguro) - icms crédito) / (1-aliq. interna) * (aliq. interna - aliq. interestadual)

    icms tributado real/presumido:
    ((v.prod + v.ipi + v.frete + v.seguro) - icms crédito) / (1 - aliq. interna) * (1 + mva cnae) * (aliq. interna) - (icms crédito)

    icms uso e consumo/ativo fixo:
    ((v.prod + v.ipi + v.frete + v.seguro) - icms crédito) / (1 - aliq.interna) * (aliq. interna - aliq. interestadual)

    icms redução:
    ((v.prod + v.ipi + v.frete + v.seguro) - icms crédito) / (1 - aliq.interna) * (1 + mva cnae) * (aliq. redução) - icms crédito


    quero ter uma aba separada para poder fazer os calculos de cesta básica que vai ser assim:

    icms cesta basica:
    separar produtos que forem cesta basica para decidir a pauta e a carga tributária do produto.
        se for maior que a pauta - (v.prod * carga tributária)
        se for menor que a pauta - (exemplo com produto em kg. valor do kilo * quantidade * carga tributária)


    a carga tributária será de acordo com essas informações e o valor dos produtos de acordo com a pauta será de acordo com o link em baixo:

    1. PRODUTOS COMPONENTES DA CESTA BÁSICA
    Decreto nº 26.145/2003, Anexo único
    São produtos componentes da cesta básica:
     feijão;
     farinha de mandioca;
     goma de mandioca;
     massa de mandioca;
     charque;
     fubá de milho ou produto similar que se preste à fabricação de cuscuz;
     leite em pó:
     embalado em sacos de até 200g;
     em embalagem igual ou superior a 25Kg, importado do exterior e destinado a posterior acondicionamento em
    sacos de até 200g;
     sal de cozinha;
     pescado não enlatado e não cozido, exceto molusco, rã, crustáceo e tilápia (veja também informativo fiscal
    "Pescados");
     sabão em tabletes de até 500g, exceto sabonete;
     sardinha em lata;
     batata inglesa, exceto quando submetida a qualquer processo de industrialização;
     pó para preparo de bebida láctea embalado em sacos de até 200g.
    IMPORTANTE:
    1. Flocos de arroz, embora se prestem a fabricação de cuscuz, e xerém de milho não são produtos componentes da
    cesta básica (Acórdão Pleno nº 0085/2008 e Decisão TATE 00.298/07-7).
    2. Sal do Himalaia (sal rosa) e sal marinho são produtos componentes da cesta básica (Resolução de Consulta nº 68/2022).
    3. Sal grosso e sal para churrasco são produtos componentes da cesta básica (Resolução de Consulta nº 70/2022; Decisão
    TATE 00.707/17-1, Acórdão 2º TJ 187/2017; Decisão TATE 00.388/21-1, Decisão JT nº 0374/2021; Decisão TATE 01.097/16-4, Acórdão 1ª TJ
    0038/2019).
    4. Sal Light não é produto componente da cesta básica (Recurso Ordinário Referente ao Acórdão 2º TJ 187/2017 e Acórdão Pleno
    0070/2018).
    5. Goma de tapioca e tapioca granulada são nomes comerciais do produto goma de mandioca, e portanto, são
    produtos componentes da cesta básica (Resolução de Consulta nº 80/2022).
    6. Polvilho doce e fécula de mandioca não são produtos componentes da cesta básica (Resolução de Consulta nº 80/2022)
    7. Jerked Beef é produto da cesta básica (Recurso Ordinário – Decisão JT nº 0912/2022; Processo TATE 00.757/22-5).
    2 PRODUTOS DA CESTA BÁSICA COM ISENÇÃO DE ICMS
    Decreto 44.650/2017, Anexo 7, art. 74; Decreto nº 26.145/2003, art. 2º, § 4º; Decreto 44.773/2017, Anexo 4, art. 1º; e Portaria SF nº 194/2017, art.
    3º, I
    Os seguintes produtos componentes da cesta básica possuem isenção de ICMS, conforme descrito abaixo:
    2.1 Farinha de mandioca
    As operações internas com farinha de mandioca estão isentas de ICMS (Decreto 44.650/2017, Anexo 7, art. 74)
    2.2 Peixe em estado natural, resfriado, congelado ou filetado, classificado nas posições 03.02, 03.03 ou 03.04
    da NBM/SH
    A saída interna de peixe em estado natural, resfriado, congelado ou filetado, classificado nas posições 03.02, 03.03
    ou 03.04 da NBM/SH, incluídos no item IX do Anexo Único do Decreto 26.145/2003, promovida por estabelecimento
    CESTA BÁSICA
    6
    produtor ou industrial, estarão isentas de ICMS desde que observados os seguintes procedimentos (Decreto 26.145/2003,
    art. 2º, § 4º):
     registrar o início da utilização deste benefício fiscal no livro Registro de Utilização de Documentos Fiscais e
    Termos de Ocorrência – RUDFTO (Portaria SF nº 194/2017, art. 3º, I, “b”)
     relativamente ao estabelecimento produtor (Decreto nº 26.145/2003, art. 2º, § 4º, I):
     o desembarque do produto deve ser feito neste Estado; e
     a isenção aplica-se à saída destinada a estabelecimento comercial ou industrial.
     relativamente ao estabelecimento industrial (Decreto nº 26.145/2003, art. 2º, § 4º, II):
     a aquisição de peixe deve estar contemplada com a isenção citada acima (ao estabelecimento produtor); e
     o processo de industrialização deve ser realizado neste Estado.
     o benefício não se aplica a bacalhau, salmão, hadoque, truta, linguado, merluza e peixes de água doce da região
    amazônica (Decreto nº 26.145/2003, art. 2º, § 4º, III).
    2.3 Sardinha (NBM/SH, 0303.53.00), cavalinha (NBM/SH, 0303.54.00) e carapau (NBM/SH 0303.55.00)
    De 01/01/2018 até 31/12/2032, as importações de sardinha (NBM/SH, 0303.53.00), cavalinha (NBM/SH, 0303.54.00)
    e carapau (NBM/SH 0303.55.00), por estabelecimento produtor, quando destinados à utilização (consumo) como
    iscas em pesca marinha, terão isenção de ICMS (Decreto 44.773/2017, Anexo 4, art. 1º; Decreto 44.650/2016, Anexo 7, art. 126).
    O contribuinte que iniciar a utilização deste benefício deve comunicar esta circunstância ao órgão da Secretaria da
    Fazenda – Sefaz responsável pelo controle e acompanhamento de benefícios fiscais (DBF) (Portaria SF nº 194/2017, art.
    1º, V).
    3. AQUISIÇÃO EM OUTRA UNIDADE DA FEDERAÇÃO
    Decreto nº 26.145/2003, art. 1º, I; art. 4º; e art. 5º, I; Decreto nº 44.650/2017, art. 2º-A
    Os contribuintes deste Estado que adquirirem produtos da cesta básica em outra Unidade da Federação, inclusive
    recebidos por transferência, recolhem antecipadamente o imposto relativo às sucessivas saídas internas, com
    exceção dos produtos que tenham isenção na respectiva saída interna.
    3.1 Cálculo do imposto antecipado
    Decreto nº 26.145/2003, art. 1º, I; art. 4º; e art. 5º, I
    A base de cálculo do imposto antecipado relativo aos produtos da cesta básica deve ser reduzida de tal forma que a
    carga tributária efetiva corresponda ao resultado da aplicação sobre o valor da operação de aquisição ou sobre o
    valor da pauta fiscal ,quando houver, dos dois o maior, de um dos percentuais a seguir indicados.
    Observar que nas cargas tributárias estabelecidas abaixo já estão computados todos os créditos fiscais.
    3.1.1 Feijão
     em embalagem de até 5kg:
     procedente das Regiões Norte, Nordeste ou Centro Oeste e do Estado do Espírito Santo: 5%
     procedente das Regiões Sul e Sudeste, exceto do Espírito Santo: 10%.
     em embalagem acima de 5kg: 2,5%
    IMPORTANTE;
    Resolução de Consulta nº 45/2023
    Feijão em embalagens de 1Kg que por conveniência e logística de transporte estejam acondionadas em
    embalagem contendo 10 sacos de 1Kg continua sendo feijão em embalagens de até 5kg, e sujeito à antecipação
    de 5% ou 10%, conforme o caso, nas aquisições em outra UF.
    3.1.2 Pescado não enlatado e não cozido, exceto molusco, rã, crustáceo e tilápia
     peixe fresco, resfriado ou congelado, classificado nas posições 03.02 ou 03.03 da NBM/SH, adquirido por
    CESTA BÁSICA
    7
    estabelecimento industrial credenciado nos termos da Portaria SF n° 59/2014: 2,5%
     demais hipóteses: 4%
    IMPORTANTE:
    Decreto n° 26.145/2003, art. 1°, § 4°
    1. A carga tributária de 2,5% do referido pescado somente se aplica ao estabelecimento industrial credenciado pela
    Diretoria Geral de Planejamento da Ação Fiscal – DPC que realize a evisceração ou filetagem, vedada a remessa
    para industrialização em outra Unidade da Federação.
    2. Na saída do produto sem que tenha sido submetido à evisceração ou filetagem ou na sua remessa para
    industrialização em outra UF, o industrial deverá efetuar a complementação do imposto devido, tomando como
    base a carga tributária prevista para as demais hipóteses (4%). A diferença será recolhida em DAE específico, sob
    o código de receita 058-2, com os acréscimos legais cabíveis, considerando-se como termo inicial o período fiscal
    em que tenha ocorrido a aquisição da mercadoria.
    3.1.3 Demais produtos
     2,5%.                para essa parte voce pode se basear bem basico de maneira com que voce modifique com as especificacoes anteriores De: Luis Miguel

    ✅ FASES DO SISTEMA:
    🧱 1. Estrutura do Projeto

    icms_fronteira/
    │
    ├── main.py                         # Inicia a interface
    ├── leitor_xml.py                  # Lê os XMLs e extrai informações relevantes
    ├── calculadora_icms.py            # Realiza todos os cálculos de ICMS
    ├── gerenciador_empresas.py        # Lida com múltiplas empresas
    ├── historico_calculos.py          # Salva e carrega os cálculos por nota
    ├── config.json                    # Armazena configurações como alíquotas padrão
    ├── pasta_empresa/                 # Estrutura padrão com XMLs por competência
    │   └── XMLs das notas...
    ├── cesta_basica.py                # Calculadora separada para itens de cesta básica
    └── util.py                        # Funções auxiliares (converter %, validar etc)

    💻 2. Tela Principal (GUI)

    Seleção da empresa pelo nome

    Caminho raiz fixo Z:\Fiscal\Simples Nacional\

    Seleção de ano e competência (ex: "2025" / "05.2025")

    Listar os XMLs da pasta notas

    Selecionar nota → abrir cálculo

    Botão "Novo cálculo"

        Botão "Ver histórico"

    📊 3. Tela de Cálculo da Nota

        Exibe:

            vProd, vIPI, vFrete, vSeg, vICMS, vDesc, vICMSST

            CRT (pra detectar se fornecedor é simples ou normal)

        Inputs editáveis:

            MVA Original (%)

            MVA CNAE (%)

            Difal Simples (%)

            Crédito ICMS (%)

            Alíquota Redução (%)

            Alíquota Interna (20,5%, mas pode mudar)

            Alíquota Interestadual (vem do XML, mas editável)

        Botões:

            [✓] Considerar desconto?

            [✓] Usar crédito manual ou destacado?

        Exibe todos os cálculos possíveis:

            ICMS ST

            ICMS Tributado (Simples e Real/Presumido)

            ICMS Uso e Consumo / Ativo Fixo

            ICMS Redução

        [✓] Histórico de cada cálculo salvo em tabela

            Data/hora, tipo de cálculo, valores usados

            Pode editar ou excluir cálculos

    🧺 4. Tela Cesta Básica (Separada)

        Lista todos os produtos da nota

        Filtra os que fazem parte da cesta básica

        Mostra:

            Valor da pauta

            Carga tributária aplicável

            Valor do imposto a recolher

        Regras aplicadas:

            Se valor do produto > pauta → usa pauta

            Se valor < pauta → usa valor real

        Usa os percentuais conforme a origem:

            Feijão (Norte/Nordeste = 5%, Sul/Sudeste = 10%)

            Pescado (4% ou 2,5% dependendo do tipo)

            Outros = 2,5%

    💾 5. Salvamento dos Cálculos

        Todos os cálculos salvos por XML (baseado na chave da nota)

        Permite mais de um cálculo por nota

        Armazenado em JSON ou SQLite (tu escolhe)

        Pode reabrir e editar qualquer cálculo depois

    📦 6. Extras

        Exporta cálculo em PDF se quiser

        Tela para cadastrar alíquotas padrão por empresa

        Suporte futuro pra integração com Excel ou API do Domínio



















Principais Faltas no Sistema Atual
Navegação entre telas

Não há menus ou botões para alternar entre a tela principal, cálculo de nota e cesta básica

Falta o sistema de seleção de empresa/ano/competência mencionado nos requisitos

Funcionalidades de cálculo incompletas

A tela mostra apenas ICMS básico e cesta básica

Faltam os outros tipos de cálculo mencionados (ICMS ST, Uso/Consumo, Redução, etc.)

Não há opções para editar parâmetros como MVA, Difal, créditos

Histórico e salvamento

Não há evidência do sistema de histórico de cálculos

Faltam botões para salvar/exportar os cálculos

Não mostra a funcionalidade de múltiplos cálculos por nota

Interface do usuário

Layout muito básico, parece mais um protótipo

Faltam elementos de GUI como menus, barras de ferramentas, status bar

Não há indicação de como criar um novo cálculo

Funcionalidades extras

Exportação para PDF não implementada

Cadastro de alíquotas padrão por empresa não visível

Integração com Excel/API não presente

Recomendações de Melhoria
Implementar um sistema de navegação entre telas com:

Menu principal

Barra de ferramentas com atalhos

Breadcrumbs para orientação do usuário

Completar todas as funcionalidades de cálculo:

Adicionar abas/seções para cada tipo de cálculo

Implementar os campos editáveis para todos os parâmetros

Desenvolver o sistema de histórico:

Banco de dados SQLite para armazenamento

Tela de visualização/edição do histórico

Controle de versões para cada cálculo

Melhorar a interface:

Adotar um framework GUI moderno

Adicionar elementos visuais para melhor usabilidade

Implementar validação de dados e feedback visual

Adicionar funcionalidades extras:

Exportação para PDF/Excel

Tela de configurações/parâmetros padrão

Sistema de ajuda/documentação