import unicodedata
import re
import string
from typing import Generator

STRING_CARACTERES_ESPECIAIS_PADRAO = string.punctuation

CARACTERES_NORMAIS : str = string.printable + 'áàâãéèêíìîóòôõúùûüç' + 'áàâãéèêíìîóòôõúùûüç'.upper() + '\xa0' # + '\xa0' representa o "espaço em branco não quebrável" em hexadecimal

LISTA_STOPWORDS_PADRAO_FREQUENCIA : list = ['a','à','as','às','ao','aos','da','das','na','nas','numa','numas',
                                            'o','os','ou','do','dos','no','nos',
                                            'de','e','é','ser','será','serão','são','está','estão','foi','em','num','nuns',
                                            'são','sem','mais','menos',
                                            'um','uma','uns','umas',
                                            'sua','suas','seu','seus',
                                            'nosso','nossos','nossa','nossas',
                                            'esse','esses','essa','essas',
                                            'só','tão','tem','tens','nem','isso','tá','ta','eu','isto','mas',
                                            'sempre','nunca',
                                            'pelo','também','já','você','vocês','vc','vcs',
                                            'ele','eles','ela','elas','nele','neles','nela','nelas',
                                            'se','te','que','por','pro','pros','pra','pras','para','com','como','sobre','sim','não']

LISTA_STOPWORDS_PADRAO_TOKENIZACAO : list = ['a','à','as','às','ao','aos','da','das','na','nas','numa','numas',
                                             'o','os','ou','do','dos','no','nos',
                                             'de','e','em','num','nuns','será','seres',
                                             'sua','suas','seu','seus',
                                             'minha','minhas','meu','meus',
                                             'teu','teus','tua','tuas',
                                             'nosso','nossos','nossa','nossas',
                                             'esse','esses','essa','essas',
                                             'só','tão','isso','isto','mas',
                                             'ele','eles','ela','elas','nele','neles','nela','nelas',
                                             'se','te','me','esta',
                                             'que','por','pro','pros','pra','pras','com','como','sobre','sob',
                                             'também','já','há']

LISTA_PONTOS_FINAIS_PADRAO_FRASES : list = ['.','!','?',';',':']

DIGITO_DIA : str = r'(0?[1-9]|1[0-9]|2[0-9]|3[0-1])'
DIGITO_MES : str = r'(0?[1-9]|1[0-2])'
DIGITO_ANO : str = r'\d{2,4}'
PADRAO_REGEX_DATA : str = r'\b{dia}\/{mes}\/{ano}\b|\b{ano}\/{mes}\/{dia}\b|\b{dia}\-{mes}\-{ano}\b|\b{ano}\-{mes}\-{dia}\b'.format(dia=DIGITO_DIA,mes=DIGITO_MES,ano=DIGITO_ANO)

PADRAO_REGEX_EMAIL : str = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

DDD_PAIS : str = r'(\+(\s+)?)?\d{2,3}'
DDD_ESTADO : str = r'(\((\s+)?)?\d{2}((\s+)?\))?'
DDD_CELULAR : str = r'\d{4,5}([-\s])?\d{4}'
PADRAO_REGEX_TELEFONE_CELULAR : str = r'({pais})?({estado})({celular})|({pais}(\s+)?)?({estado}(\s+)?)({celular})'.format(pais=DDD_PAIS,estado=DDD_ESTADO,celular=DDD_CELULAR)

PADRAO_REGEX_LINKS : str = r'https?://\S+'

PADRAO_REGEX_NUMEROS : str = r'(\b)?\d+(\S+)?(,\d+)?(\b)?|(\b)?\d+(\S+)?(.\d+)?(\b)?'

PADRAO_REGEX_DINHEIRO : str = r'R\$(\s+)?\d+(\S+)?(,\d{2})?|\$(\s+)?\d+(\S+)?(\.\d{2})?'

PADRAO_REGEX_CPF : str = r'(\b)\d{3}\.\d{3}\.\d{3}-\d{2}(\b)'

PADRAO_REGEX_CEP : str = r'(\b)\d{5}\-\d{3}(\b)'

PADRAO_REGEX_RG : str = r'(\b)\d\.\d{3}.\d{3}(\b)'

DICIONARIO_CONFIG_PADRAO_TOKENIZACAO = {'removerCaracteresEstranhos':True,'removerEspacosEmBrancoExtras':True,'padronizarTextoParaMinuscula':True,'removerCaracteresEspeciais':[True,STRING_CARACTERES_ESPECIAIS_PADRAO]}

def coletarTextoDeArquivoTxt(caminho_arquivo : str,
                             tipo_de_encoding : str = 'utf-8') -> str | None:
    """
    ### Objetivo
    Essa função tem como objetivo retornar o conteúdo textual de um arquivo ".txt".

    ### Parâmetros:
    - caminho_arquivo: String referente ao caminho onde o arquivo está armazenado.
    - tipo_de_encoding: String contendo o tipo de codificação utilizado no arquivo (padrão foi deixado em "utf-8").
    ### Retornos:
    - return: String contendo o conteúdo textual do arquivo, caso o consiga abrir e ler, ou None caso ocorra um erro nestes processos.
    """
    if caminho_arquivo.endswith('.txt'):
        try:
            with open(caminho_arquivo,'r',encoding=tipo_de_encoding) as f:
                texto = f.read()
        except Exception as e:
            erro = f'{e.__class__.__name__}: {str(e)}'
            print(f'Ocorreu um erro ao abrir o arquivo "{caminho_arquivo}".\n--> {erro}')
            return None
        else:
            return texto
    else:
        return None

def removerCaracteresEspeciais(texto : str,                              
                               string_caracteres_especiais : str = STRING_CARACTERES_ESPECIAIS_PADRAO,                               
                               remover_espacos_em_branco_extras : bool = True,
                               remover_hifen_de_palavras : bool = False,
                               tratamento_personalizado : bool = True) -> str:
    """
    ## Objetivo
    Esta função remove caracteres presentes na lista de caracteres para remoção fornecida 
    da string de texto fornecida.
    
    
    FALTA ATUALIZAR DOC STRING!!!!!!!!!!! (adc remover_hifen_de_palavras)
    

    ## Parâmetros
    - :parâmetro texto: String que você quer limpar dos caracteres especiais.
    - :parâmetro string_caracteres_especiais: String contendo todos os 
    caracteres especiais que você quer remover da string de texto fornecida (o 
    padrão é a string "!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~".

    ## Retornos:    
    - :retorno: String fornecida sem os caracteres especiais.
    """
    if not remover_hifen_de_palavras:
        string_caracteres_especiais = string_caracteres_especiais.replace('-','')
        texto = texto.replace(' -',' ').replace('- ',' ')
    if not tratamento_personalizado:
        texto = texto.translate(str.maketrans('','',string_caracteres_especiais))
    else:
        if remover_hifen_de_palavras:
            string_caracteres_especiais_ad_espaco = r'\/\\\-'
        else:
            string_caracteres_especiais_ad_espaco = r'\/\\'
        texto = texto.translate(str.maketrans(string_caracteres_especiais_ad_espaco,' '*len(string_caracteres_especiais_ad_espaco)))
        texto = texto.translate(str.maketrans('','',string_caracteres_especiais))
    if remover_espacos_em_branco_extras:
        texto = removerEspacosEmBrancoExtras(texto)
    return texto

def removerCaracteresEstranhos(texto : str) -> str:
    """
    Esta função passa por todos os caracteres presentes na string de texto 
    fornecida e, se o caracter não estiver dentro da string "CARACTERES_NORMAIS", 
    a qual é basicamente:
    "string.printable + 'áàâãéèêíìîóòôõúùûç' + 'áàâãéèêíìîóòôõúùûç'.upper()",
    remove-o da string original.

    ### Parâmetros:
    - :parâmetro texto: String contendo o texto que você quer limpar.

    ### Retornos:
    - :retorno: String limpa dos caracteres "mais que especiais" (emojis, dígitos estranhos, 
    formas que não se encontram no teclado, etc).
    """
    for caracter_estranho in [c for c in texto if c not in CARACTERES_NORMAIS]:
        texto = texto.replace(caracter_estranho,'')
    return texto

def removerEspacosEmBrancoExtras(texto : str) -> str:
    """
    ### Objetivo
    Remover espaços em branco em excesso (dois ou mais em sequência) no texto fornecido como entrada.

    ### Parâmetros:
    - texto: String contendo o texto que você quer modificar.

    ### Retornos:
    - :return: String modificada, ou seja, sem espaços em branco extras caso os encontre.
    """
    return re.sub(r'[^\S\n]+',' ',texto)

def transformarTextoSubstituindoCaracteres(texto : str,
                                           caracteres : str | list[str],
                                           substituir_por : str = '',
                                           contagem : int = 0,
                                           considerar_maiusculas_e_minusculas_iguais : bool = False) -> str:
    """
    Esta função remove os caracteres específicos de sua escolha da string de texto fornecida, 
    com base nas regras que você define usando os parâmetros.

    Parâmetros
    ----------
    - :parâmetro texto: String contendo o texto que você quer transformar.
    - :parâmetro caracteres: String contendo o caracter (ou caracteres, se for uma palavra) que 
    você deseja substituir.
    - :parâmetro substituir_por: String contendo o caracter (ou os caracteres, se for uma palavra) 
    que você deseja botar no lugar dos caracteres que você deseja substituir.
    - :parâmetro contagem: Número de vezes referente à remoção do(s) caracter(es) escolhido(s) toda 
    vez que ele for encontrado na string de texto fornecida (o valor padrão é -1, que indica que 
    serão removidos todas as aparições, mas também poderá ser escolhido como contagem = 0 se você 
    quer que seja removido apenas a última aparição). A ordem da contagem é sempre do início para o 
    fim da string de texto.
    - :parâmetro considerar_maiusculas_e_minusculas_iguais: Bool que dirá se você quer considerar 
    as letras maiúscula e minúsculas como iguais (True) ou não (False).
    Retornos
    --------
    - :retorno: String fornecida sem os caracteres escolhidos.
    """
    if isinstance(caracteres,str):
        for c in caracteres:
            if c in string.punctuation:
                caracteres = caracteres.replace(c,r'\{x}'.format(x=c))
    if contagem == -1:        
        if isinstance(caracteres,str):
            if considerar_maiusculas_e_minusculas_iguais:
                texto_analisado = texto.lower()
                caracteres = caracteres.lower()
            else:
                texto_analisado = texto

            resultado = [indice.start() for indice in re.finditer(r'{}'.format(caracteres),texto_analisado)]
            if resultado:
                texto = texto[:resultado[-1]]+substituir_por+texto[resultado[-1]+1:]
            return texto
        
        elif isinstance(caracteres,list):
            padrao_regex_caracteres_na_lista = r''
            for caracter in caracteres:
                if caracter in string.punctuation:
                    caracter = r'\{x}'.format(x=caracter)
                padrao_regex_caracteres_na_lista += r'{x}|'.format(x=caracter)
            padrao_regex_caracteres_na_lista = padrao_regex_caracteres_na_lista[0:-1]
            if considerar_maiusculas_e_minusculas_iguais:
                resultado = [indice.start() for indice in re.finditer(padrao_regex_caracteres_na_lista,texto,flags=re.IGNORECASE)]
            else:
                resultado = [indice.start() for indice in re.finditer(padrao_regex_caracteres_na_lista,texto)]
            if resultado:
                texto = texto[:resultado[-1]]+substituir_por+texto[resultado[-1]+1:]
            return texto
    else:
        if isinstance(caracteres,str):
            if considerar_maiusculas_e_minusculas_iguais:
                return re.sub(r'{c}'.format(c=caracteres),substituir_por,string=texto,count=contagem,flags=re.IGNORECASE)
            else:
                return re.sub(r'{c}'.format(c=caracteres),substituir_por,string=texto,count=contagem)
        elif isinstance(caracteres,list):
            padrao_regex_caracteres_na_lista = r''
            for caracter in caracteres:
                if caracter in string.punctuation:
                    caracter = r'\{x}'.format(x=caracter)
                padrao_regex_caracteres_na_lista += r'{x}|'.format(x=caracter)
            padrao_regex_caracteres_na_lista = padrao_regex_caracteres_na_lista[0:-1]
            if considerar_maiusculas_e_minusculas_iguais:
                return re.sub(padrao_regex_caracteres_na_lista,substituir_por,string=texto,count=contagem,flags=re.IGNORECASE)
            else:
                return re.sub(padrao_regex_caracteres_na_lista,substituir_por,string=texto,count=contagem)

def verificarExistenciaDeElemento(texto : str,
                                  string_especifica : str | None = None,
                                  encontrar_datas : bool = False,                                  
                                  encontrar_emails : bool = False,
                                  encontrar_telefone_celular : bool = False,
                                  encontrar_links : bool = False,
                                  encontrar_numeros : bool = False,
                                  encontrar_dinheiro : bool = False,
                                  considerar_maiusculas_e_minusculas_iguais : bool = True) -> bool:
    
    if string_especifica:
        for c in string_especifica:
            if c in string_especifica:
                string_especifica.replace(c,r'\{x}'.format(x=c))
        if considerar_maiusculas_e_minusculas_iguais:
            if re.search(r'{x}'.format(x=string_especifica),texto,flags=re.IGNORECASE):
                return True
            else:
                return False
        else:
            if re.search(r'{x}'.format(x=string_especifica),texto):
                return True
            else:
                return False
    if encontrar_datas:
        if re.search(PADRAO_REGEX_DATA,texto):
            return True
        else:
            return False
    if encontrar_emails:
        if re.search(PADRAO_REGEX_EMAIL,texto):
            return True
        else:
            return False
    if encontrar_telefone_celular:
        if re.search(PADRAO_REGEX_TELEFONE_CELULAR,texto):
            return True
        else:
            return False
    if encontrar_links:
        if re.search(PADRAO_REGEX_LINKS,texto):
            return True
        else:
            return False
    if encontrar_numeros:
        if re.search(PADRAO_REGEX_NUMEROS,texto):
            return True
        else:
            return False
    if encontrar_dinheiro:
        if re.search(PADRAO_REGEX_DINHEIRO,texto):
            return True
        else:
            return False
         


def padronizarRG(texto: str,
                 padrao_rg : str = 'RG') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em RG do tipo "0.000.000"
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de RG.
    - padrao_rg: String que ocupará o lugar dos caracteres referentes ao RG, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de RG.
    """
    return re.sub(PADRAO_REGEX_RG,padrao_rg,texto)

def padronizarCPF(texto: str,
                  padrao_cpf : str = 'CPF') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em CPF do tipo "000.000.000-00"
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de CPF.
    - padrao_cpf: String que ocupará o lugar dos caracteres referentes ao CPF, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de CPF.
    """
    return re.sub(PADRAO_REGEX_CPF,padrao_cpf,texto)

def padronizarCEP(texto: str,
                  padrao_cep : str = 'CEP') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em CEP do tipo "00000-000"
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de CEP.
    - padrao_cep: String que ocupará o lugar dos caracteres referentes ao CEP, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de CEP.
    """
    return re.sub(PADRAO_REGEX_CEP,padrao_cep,texto)

def padronizarDatas(texto: str,
                    padrao_data : str = 'DATA') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em DATAS das variações de tipo "12/12/2024", "2024/12/12", "12-12-2024", "2024-12-12".
    Para mais informações sobre os padrões de data alcançados, utilizar a constante PADRAO_REGEX_DATA, a qual armazena a expressão regex das datas.
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de RG.
    - padrao_data: String que ocupará o lugar dos caracteres referentes à DATAS, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de data.
    """
    return re.sub(PADRAO_REGEX_DATA,padrao_data,texto)

def padronizarEmails(texto : str,
                     padrao_email : str = 'EMAIL') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em EMAILS das variações de tipo "@gmail.com", "@hotmail.com", "@yahoo.com.br", etc.
    Para mais informações sobre os padrões de emails alcançados, utilizar a constante PADRAO_REGEX_EMAIL, a qual armazena a expressão regex dos emails.
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de RG.
    - padrao_email: String que ocupará o lugar dos caracteres referentes aos EMAILS, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de email.
    """
    return re.sub(PADRAO_REGEX_EMAIL,padrao_email,texto)

def padronizarTelefoneCelular(texto : str,
                              padrao_tel : str = 'TEL') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em TELEFONE/CELULAR das variações de tipo "+55 48 90011-2233", "(48) 90011-2233", "0011-2233", etc.
    Para mais informações sobre os padrões de telefone/celular alcançados, utilizar a constante PADRAO_REGEX_TELEFONE_CELULAR, a qual armazena a expressão regex dos telefones e celulares.
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de RG.
    - padrao_tel: String que ocupará o lugar dos caracteres referentes aos TELEFONES/CELULARES, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de telefone/celular.
    """
    return re.sub(PADRAO_REGEX_TELEFONE_CELULAR,padrao_tel,texto)

def padronizarLinks(texto : str,
                    padrao_link : str = 'LINK') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em URLs do tipo "http://..." ou "https://..."
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de LINK.
    - padrao_link: String que ocupará o lugar dos caracteres referentes aos LINKS, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de link.
    """
    return re.sub(PADRAO_REGEX_LINKS,padrao_link,texto)

def padronizarNumeros(texto : str,
                      padrao_numeros : str = 'NUM') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em NUMEROS das variações de tipo "1.000", "1.000,00","1.000.000.000,00", etc.
    Para mais informações sobre os padrões de número alcançados, utilizar a constante PADRAO_REGEX_NUMEROS, a qual armazena a expressão regex dos números.
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de NUMERO.
    - padrao_numeros: String que ocupará o lugar dos caracteres referentes aos NUMEROS, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de numero.
    """
    return re.sub(PADRAO_REGEX_NUMEROS,padrao_numeros,texto)

def padronizarDinheiros(texto : str,
                        padrao_dinheiro : str = '$') -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem em DINHEIRO das variações de tipo "R$ 10", "R$ 10,00", "R$ 1.000","R$   10.000.000.000,00", etc.
    Para mais informações sobre os padrões de dinheiro alcançados, utilizar a constante PADRAO_REGEX_DINHEIRO, a qual armazena a expressão regex de dinheiro.
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que contém o padrão de DINHEIRO.
    - padrao_dinheiro: String que ocupará o lugar dos caracteres referentes aos DINHEIROS, mascarando-os.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres no padrão de dinheiro.
    """ 
    return re.sub(PADRAO_REGEX_DINHEIRO,padrao_dinheiro,texto)


def normalizarTexto(texto : str) -> str:
    """
    ### Objetivo
    Função destinada à padronizar os elementos no texto que se caracterizem por possuir acentos, "ç", etc, passando-os para a forma mais "normal" destes.
    Exemplo: "ação" padronizado para a forma canonica ficaria "acao".
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que não estão na forma canônica.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres que não estão na forma canônica.
    """
    return ''.join(c for c in (d for char in texto for d in unicodedata.normalize('NFD', char) if unicodedata.category(d) != 'Mn'))


def padronizarTextoParaMinuscula(texto : str) -> str:
    """
    ### Objetivo
    Função destinada à padronizar os caracteres nos texto para minúscula.
    Exemplo: "PrograMaR" padronizado para minúsculas ficaria "programar".
    ### Parâmetros:
    - texto: String fornecida de entrada, para alterar os caracteres que não estão em minúscula.
    ### Retornos:
    - return: String do texto modificado, caso encontre caracteres que não estão em minúscula.
    """
    return texto.lower()




def contarFrequenciaDePalavras(texto : str | list,
                               palavras_especificas : list[str] | None = None,
                               n_top : int = -1,
                               remover_palavras_de_escape : bool = True,
                               lista_stopwords : list = LISTA_STOPWORDS_PADRAO_FREQUENCIA,
                               tratamento_padrao : bool = True) -> list:    

    lista_tokenizada = tokenizarTexto(texto=texto,remover_palavras_de_escape=remover_palavras_de_escape,lista_stopwords=lista_stopwords,tratamento_padrao=tratamento_padrao)
    dic = {}
    if palavras_especificas:
        if isinstance(lista_tokenizada[0],str):
            for token in palavras_especificas:
                if token not in dic.keys():
                    dic[token] = lista_tokenizada.count(token)
        elif isinstance(lista_tokenizada[0],list):
            for frase in lista_tokenizada:
                tokens_usados = []
                for token in palavras_especificas:
                    if token not in tokens_usados:
                        if token not in dic.keys():
                            dic[token] = frase.count(token)
                    else:
                        dic[token] += frase.count(token)
    else:
        if lista_tokenizada:
            if isinstance(lista_tokenizada[0],str):
                for token in lista_tokenizada:
                    if token not in dic.keys():
                        dic[token] = lista_tokenizada.count(token)
            elif isinstance(lista_tokenizada[0],list):
                for frase in lista_tokenizada:
                    for token in frase:
                        if token not in dic.keys():
                            dic[token] = frase.count(token)                        
    lista_de_frequencias = []
    for token in dic.keys():
        frequencia_do_token = dic[token]
        lista_de_frequencias.append((token,frequencia_do_token))
    
    lista_de_frequencias = sorted(lista_de_frequencias, key=lambda x: x[1], reverse=True)

    if n_top != -1:
        lista_de_frequencias = lista_de_frequencias[:n_top]

    return lista_de_frequencias

def formatarTexto(texto : str,
                  padronizar_texto_para_minuscula : bool = True,
                  remover_caracteres_estranhos : bool = True,
                  remover_caracteres_especiais : bool = True,
                  string_caracteres_especiais : str = STRING_CARACTERES_ESPECIAIS_PADRAO,
                  remover_espacos_em_branco_em_excesso : bool = True,
                  padronizar_cpf : bool = False,
                  padrao_cpf : str = 'CPF',
                  padronizar_rg : bool = False,
                  padrao_rg : str = 'RG',
                  padronizar_cep : bool = False,
                  padrao_cep : str = 'CEP',
                  padronizar_links : bool = False,
                  padrao_link : str = 'LINK',
                  padronizar_numeros : bool = False,
                  padrao_numero : str = 'NUM',
                  padronizar_dinheiros : bool = False,
                  padrao_dinheiro : str = '$',
                  padronizar_datas : bool = False,
                  padrao_data : str = 'DATA',
                  padronizar_emails : bool = False,
                  padrao_email : str = 'EMAIL',
                  padronizar_telefone_celular : bool = False,
                  padrao_tel : str = 'TEL',
                  normalizar : bool = False) -> str:
    if remover_caracteres_estranhos:
        texto = removerCaracteresEstranhos(texto)
    if remover_espacos_em_branco_em_excesso:
        texto = removerEspacosEmBrancoExtras(texto)
    if padronizar_dinheiros:
        for caracter_padrao_dinheiro in padrao_dinheiro:
            if caracter_padrao_dinheiro in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_dinheiro = True
                texto = padronizarDinheiros(texto=texto,padrao_dinheiro='codpdintzzqaio')
                break
        else:
            caracteres_especiais_impacta_padrao_dinheiro = False
            texto = padronizarDinheiros(texto=texto,padrao_dinheiro=padrao_dinheiro)    
    if padronizar_links:
        for caracter_padrao_link in padrao_link:
            if caracter_padrao_link in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_link = True
                texto = padronizarLinks(texto=texto,padrao_link='codpltzzqaio')
                break
        else:
            caracteres_especiais_impacta_padrao_link = False
            texto = padronizarLinks(texto=texto,padrao_link=padrao_link)    
    if padronizar_datas:
        for caracter_padrao_data in padrao_data:
            if caracter_padrao_data in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_data = True
                texto = padronizarDatas(texto=texto,padrao_data='codpdttzzqaio')
                break
        else:
            caracteres_especiais_impacta_padrao_data = False
            texto = padronizarDatas(texto=texto,padrao_data=padrao_data)
    if padronizar_emails:
        for caracter_padrao_email in padrao_email:
            if caracter_padrao_email in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_email = True
                texto = padronizarEmails(texto=texto,padrao_email='codpemtzzqaio')
                break
        else:
            caracteres_especiais_impacta_padrao_email = False
            texto = padronizarEmails(texto=texto,padrao_email=padrao_email)
    if padronizar_telefone_celular:
        for caracter_padrao_tel in padrao_tel:
            if caracter_padrao_tel in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_tel = True
                texto = padronizarTelefoneCelular(texto=texto,padrao_tel='codptctzzqaio')
                break
        else:
            caracteres_especiais_impacta_padrao_tel = False
            texto = padronizarTelefoneCelular(texto=texto,padrao_tel=padrao_tel)
    if padronizar_rg:
        for caracter_padrao_rg in padrao_rg:
            if caracter_padrao_rg in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_rg = True
                texto = padronizarNumeros(texto=texto,padrao_cpf='codprgtzzqaio') 
                break
        else:
            caracteres_especiais_impacta_padrao_rg = False
            texto = padronizarNumeros(texto=texto,padrao_rg=padrao_rg)
    if padronizar_cpf:
        for caracter_padrao_cpf in padrao_cpf:
            if caracter_padrao_cpf in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_cpf = True
                texto = padronizarNumeros(texto=texto,padrao_cpf='codpcpftzzqaio') 
                break
        else:
            caracteres_especiais_impacta_padrao_cpf = False
            texto = padronizarNumeros(texto=texto,padrao_cpf=padrao_cpf)
    if padronizar_cep:
        for caracter_padrao_cep in padrao_cep:
            if caracter_padrao_cep in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_cep = True
                texto = padronizarNumeros(texto=texto,padrao_cep='codpceptzzqaio') 
                break
        else:
            caracteres_especiais_impacta_padrao_cep = False
            texto = padronizarNumeros(texto=texto,padrao_cep=padrao_cep)        
    if padronizar_numeros:
        for caracter_padrao_numero in padrao_numero:
            if caracter_padrao_numero in string_caracteres_especiais:
                caracteres_especiais_impacta_padrao_numero = True
                texto = padronizarNumeros(texto=texto,padrao_numeros='codpntzzqaio') 
                break
        else:
            caracteres_especiais_impacta_padrao_numero = False
            texto = padronizarNumeros(texto=texto,padrao_numeros=padrao_numero)

    if remover_caracteres_especiais:
        texto = removerCaracteresEspeciais(texto=texto,
                                           string_caracteres_especiais=string_caracteres_especiais)
       
    if padronizar_texto_para_minuscula:
        texto = padronizarTextoParaMinuscula(texto)
    if normalizar:
        texto = normalizarTexto(texto) 
    if padronizar_dinheiros and caracteres_especiais_impacta_padrao_dinheiro:
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codpdintzzqaio',substituir_por=padrao_dinheiro)
    if padronizar_links and caracteres_especiais_impacta_padrao_link:
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codpltzzqaio',substituir_por=padrao_link)
    if padronizar_numeros and caracteres_especiais_impacta_padrao_numero: 
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codpntzzqaio',substituir_por=padrao_numero)
    if padronizar_datas and caracteres_especiais_impacta_padrao_data:
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codpdttzzqaio',substituir_por=padrao_data)
    if padronizar_emails and caracteres_especiais_impacta_padrao_email:
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codpemtzzqaio',substituir_por=padrao_email)
    if padronizar_telefone_celular and caracteres_especiais_impacta_padrao_tel:
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codptctzzqaio',substituir_por=padrao_tel)
    if padronizar_cpf and caracteres_especiais_impacta_padrao_cpf: 
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codpcpftzzqaio',substituir_por=padrao_cpf)
    if padronizar_cep and caracteres_especiais_impacta_padrao_cep: 
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codpceptzzqaio',substituir_por=padrao_cep)
    if padronizar_rg and caracteres_especiais_impacta_padrao_rg: 
        texto = transformarTextoSubstituindoCaracteres(texto=texto,caracteres='codprgtzzqaio',substituir_por=padrao_rg)

    return texto



def verificarFinalDeLinha(primeira_linha : str,
                          segunda_linha : str,
                          lista_de_pontos_finais : list = LISTA_PONTOS_FINAIS_PADRAO_FRASES) -> tuple[bool, str]:
    primeira_linha = primeira_linha.strip()
    segunda_linha = segunda_linha.strip()
    for ptos_final in lista_de_pontos_finais:
        if primeira_linha.strip().endswith(ptos_final):
            if ptos_final == '.':
                if not (verificaAbreviacao(primeira_linha[-4:]) and segunda_linha[0].islower()): # Terminação em abreviação de nome e próxima linha com caracter minúsculo (continuação de frase)
                    return True, segunda_linha
                else:
                    return False, primeira_linha+' '+segunda_linha 
            else:
                return True, segunda_linha
    if primeira_linha.endswith('-') and not (segunda_linha.startswith(' ')):
        return False, primeira_linha+segunda_linha        
    else:
        return False, primeira_linha+' '+segunda_linha


def organizaTextoPelasLinhas(texto_completo : str) -> list:
    textos_separados_por_quebra_de_linha = texto_completo.split('\n')
    frases_completas_por_linha = []
    
    if textos_separados_por_quebra_de_linha:
        frases_completas_por_linha.append(removerEspacosEmBrancoExtras(textos_separados_por_quebra_de_linha[0]))    
        for linha in textos_separados_por_quebra_de_linha[1:]:
            if linha.strip() != '':
                linha = removerEspacosEmBrancoExtras(linha)
                status_final_de_linha, resultado = verificarFinalDeLinha(frases_completas_por_linha[-1],linha)
                if status_final_de_linha:
                    frases_completas_por_linha.append(resultado)
                else:
                    frases_completas_por_linha[-1] = resultado
            else:
                if frases_completas_por_linha[-1].strip()[-1] not in ['.','!','?',';']: 
                    frases_completas_por_linha[-1] += '.'

    return frases_completas_por_linha

def verificaAbreviacao(texto : str) -> bool:
    if texto[-2].isupper() and texto[-3] == ' ': # # Se terminar com a abreviação, ou por exemplo: "Igor C. de Souza" contemplaremos o "C." sem terminar a frase
        return True
    texto = texto.lower()
    for abreviacao in ['dr.','sr.','dra.','sra.','srta.',
                       'prof.','profa.','prof°.','profª.',
                       'min.','nº.', # "Ministério"
                       'pág.','pag','pg.','p.','cap.',
                       'in.','op.','cit.','fg.','fig.',
                       'vers.', 'nat.',
                       'm.','e.','dic.','abr.','id.','rubr.','univ.','med.','gên.']: # "Versículo", "Dr.rer.nat."
        if texto.endswith(abreviacao):
            return True
    return False

def separarFrasesNaMesmaLinha(frase_linha : str) -> list[str]:
    frase_linha = frase_linha.replace('(...)','')
    index_frase_final = []
    frases = []    
    i = 0
    tamanho_texto = len(frase_linha)
    while i < tamanho_texto:
        c = frase_linha[i]
        if c in ['!','?',';']:
            if i + 1 < tamanho_texto:
                if frase_linha[i+1] == ' ':
                    index_frase_final.append(i+1)
            else:
                index_frase_final.append(i+1)
        elif c == '.':
            if i + 1 < tamanho_texto:
                if not frase_linha[i+1] == '.':
                    if frase_linha[i+1] == ' ': # Elimina links e qualquer coisa que depois do ponto venha junto "1.2 google.com.br"
                        if i-7 >= 0:
                            parte_inicial = i-7
                        else:
                            parte_inicial = 0
                        if not (verificaAbreviacao(frase_linha[parte_inicial:i+1]) ): # or frase_linha[i+1].isdigit() --> Elimina abreviações e números com pontos "1.200" --> Removido, pois a regra do espaço já enquadra esta situação
                            index_frase_final.append(i)
            else:
                if i-7 >= 0:
                    parte_inicial = i-7
                else:
                    parte_inicial = 0
                if not verificaAbreviacao(frase_linha[parte_inicial:i+1]):
                    index_frase_final.append(i+1)
        i += 1
    if not index_frase_final:
        index_frase_final.append(tamanho_texto)

    for j,index in enumerate(index_frase_final):
        if j == 0:
            frases.append(frase_linha[0:index+1].strip())
        elif j == tamanho_texto - 1:
            frases.append(frase_linha[index:].strip())
        else:
            frases.append(frase_linha[index_frase_final[j-1]+1:index+1].strip())
    return frases

def tokenizarFrases(texto_completo : str) -> list[str]:
    frases_separadas = []
    for frase_linha in organizaTextoPelasLinhas(texto_completo=texto_completo):
            frases_separadas.extend(separarFrasesNaMesmaLinha(frase_linha=frase_linha))
    return frases_separadas

def tokenizadorDeFrase(frase : str,
                       remover_stopwords : bool,
                       lista_stopwords : list) -> list:
    lista_de_tokens = []
    if not isinstance(frase,str): # Contemplando o método do spaCy (para testes)
        try:
            frase = frase.orth_
        except Exception as e:
            frase = str(frase)

    if remover_stopwords:
        for token in frase.split():
            if token not in lista_stopwords:
                lista_de_tokens.append(token)
    else:
        for token in frase.split():
            lista_de_tokens.append(token)
    return lista_de_tokens

def tokenizadorDeListaDeFrasesRetornoLista(lista_de_frases : list,
                                           remover_stopwords : bool,
                                           lista_stopwords : list) -> list:
    
    lista_de_frases_tokenizadas = []
    for frase in lista_de_frases:
        lista_de_frases_tokenizadas.append(tokenizadorDeFrase(frase=frase,
                                                              remover_stopwords=remover_stopwords,
                                                              lista_stopwords=lista_stopwords))
    return lista_de_frases_tokenizadas

def tokenizadorDeListaDeFrasesRetornoGerador(lista_de_frases : list,
                                             remover_stopwords : bool,
                                             lista_stopwords : list) -> Generator:
    for frase in lista_de_frases:
        yield tokenizadorDeFrase(frase=frase,
                                 remover_stopwords=remover_stopwords,
                                 lista_stopwords=lista_stopwords)
    
def GeradorDeTokens(texto : str, 
                    remover_caracteres_especiais : bool,
                    remover_stopwords : bool, 
                    lista_stopwords : list) -> Generator:
    if remover_stopwords:
        if remover_caracteres_especiais:
            for token in removerCaracteresEspeciais(texto=texto).split():
                if token not in lista_stopwords:
                    yield token
        else:
            for token in texto.split():
                if token not in lista_stopwords:
                    yield token
    else:
        if remover_caracteres_especiais:
            for token in removerCaracteresEspeciais(texto=texto).split():                
                yield token
        else:
            for token in texto.split():
                yield token

def tokenizarTexto(texto : str,
                   dividir_frases : bool = True,
                   remover_stopwords : bool = False,
                   lista_stopwords : list = LISTA_STOPWORDS_PADRAO_TOKENIZACAO,
                   desconsiderar_acentuacao_nas_stopwords : bool = False,
                   tratamento_padrao : bool = True,
                   config_tratamento_padrao : dict = DICIONARIO_CONFIG_PADRAO_TOKENIZACAO,
                   retorno_como_gerador : bool = False) -> list | Generator:
    if desconsiderar_acentuacao_nas_stopwords:
        lista_stopwords = [normalizarTexto(elemento) for elemento in lista_stopwords]
    if tratamento_padrao:
        try:
            if config_tratamento_padrao['removerCaracteresEstranhos']:
                texto = removerCaracteresEstranhos(texto)
            if config_tratamento_padrao['removerCaracteresEspeciais'][0]:
                # texto = removerCaracteresEspeciais(texto=texto,string_caracteres_especiais=config_tratamento_padrao['removerCaracteresEspeciais'][1])
                remover_caracteres_especiais = True
            else:
                remover_caracteres_especiais = False
            if config_tratamento_padrao['padronizarTextoParaMinuscula']:
                texto = padronizarTextoParaMinuscula(texto)
            if config_tratamento_padrao['removerEspacosEmBrancoExtras']:
                texto = removerEspacosEmBrancoExtras(texto)
        except Exception as e:
            erro = f'{e.__class__.__name__}: {str(e)}'
            print(f'Erro ao realizar tratamento padrão em tokenizarTexto().\n-->{erro}.\nVerifique se configurou corretamente a variável config_tratamento_padrao.')

    if dividir_frases:

        frases_separadas = tokenizarFrases(texto_completo=texto)

        if retorno_como_gerador:            
            frases_tokenizadas = tokenizadorDeListaDeFrasesRetornoGerador(lista_de_frases=frases_separadas,remover_stopwords=remover_stopwords,lista_stopwords=lista_stopwords)
        else:
            frases_tokenizadas = tokenizadorDeListaDeFrasesRetornoLista(lista_de_frases=frases_separadas,remover_stopwords=remover_stopwords,lista_stopwords=lista_stopwords)
        
        return frases_tokenizadas
    else:
        if retorno_como_gerador:
            return GeradorDeTokens(texto=texto,remover_caracteres_especiais=remover_caracteres_especiais,remover_stopwords=remover_stopwords,lista_stopwords=lista_stopwords)
        else:
            lista_de_tokens = []

            texto_separado = texto.split()
            if remover_stopwords:
                if remover_caracteres_especiais:
                    texto_separado = removerCaracteresEspeciais(texto_separado)
                for token in texto_separado:
                    if token not in lista_stopwords:
                        lista_de_tokens.append(token)
            else:
                if remover_caracteres_especiais:
                    texto_separado = removerCaracteresEspeciais(texto_separado)
                for token in texto_separado:
                    lista_de_tokens.append(token)

            return lista_de_tokens

