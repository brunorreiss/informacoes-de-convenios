# Importando libs
# stdlib imports
from os import environ as env
from datetime import datetime
from urllib.parse import urlencode

# 3rd party imports
import aiohttp
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from fastapi import responses, status
from bs4 import BeautifulSoup

# Local imports
from src.models import *
from utils.util import get_headers

# Captura variaveis de ambiente e cria constants
TIMEOUT = env.get('TIMEOUT', default=180)

#-----------------------------------------------------------------------------------------------------
async def fetch(ano_exercicio, orgao):
    if (not ano_exercicio or not orgao):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": 422, "message": "Unprocessable Entity", 
                     "datetime": datetime.now().isoformat()}
        )
    
    orgao_dict = {
        'AGENCIA DE DESENVOLVIMENTO DA ECONOMIA DO MAR DE FORTALEZA': 11206,
        'AGENCIA DE FISCALIZACAO DE FORTALEZA': 11204,
        'AGENCIA DE REGULACAO, FISCALIZACAO E CONTROLE DOS SERVICOS PUBLICOS DE SANEAMENTO AMBIENTAL': 13201,
        'AUTARQUIA DE URBANISMO E PAISAGISMO DE FORTALEZA': 33201,
        'AUTARQUIA MUNICIPAL DE TRANSITO E CIDADANIA': 19201,
        'CAMARA MUNICIPAL DE FORTALEZA': 1101,
        'CENTRAL DE LICITACOES DA PREFEITURA DE FORTALEZA': 13102,
        'COMPANHIA DE TRANSPORTE COLETIVO - CTC': 19205,
        'CONTROLADORIA E OUVIDORIA GERAL DO MUNICIPIO': 14101,
        'COORDENADORIA ESPECIAL DE PROTECAO E BEM-ESTAR ANIMAL': 11102,
        'DEPARTAMENTO MUNICIPAL DE PROTECAO E DEFESA DOS DIREITOS DO CONSUMIDOR': 31102,
        'EMPRESA DE TRANSPORTE URBANO DE FORTALEZA': 19204,
        'FRIGORÍFICO INDUSTRIAL DE FORTALEZA S.A': 18205,
        'FUNDACAO DA CRIANCA E DA FAMILIA CIDADA': 31201,
        'FUNDACAO DE CIENCIA, TECNOLOGIA E INOVACAO DE FORTALEZA': 11205,
        'FUNDO DE APERFEICOAMENTO DA PROCURADORIA GERAL DO MUNICIPIO': 13901,
        'FUNDO DE DEFESA DO MEIO AMBIENTE': 28901,
        'FUNDO ESPECIAL DA CAMARA MUNICIPAL DE FORTALEZA': 1901,
        'FUNDO MUNICIPAL DE ASSISTENCIA SOCIAL': 31901,
        'FUNDO MUNICIPAL DE CULTURA': 32901,
        'FUNDO MUNICIPAL DE DEFESA DOS DIREITOS DA CRIANCA E DO ADOLESCENTE': 31902,
        'FUNDO MUNICIPAL DE DEFESA DOS DIREITOS DIFUSOS': 31905,
        'FUNDO MUNICIPAL DE DESENVOLVIMENTO ECONOMICO': 26901,
        'FUNDO MUNICIPAL DE DESENVOLVIMENTO URBANO': 28902,
        'FUNDO MUNICIPAL DE EDUCACAO': 24901,
        'FUNDO MUNICIPAL DE EDUCACAO ? INFRAESTRUTURA': 24902,
        'FUNDO MUNICIPAL DE HABITACAO DE INTERESSE SOCIAL': 34901,
        'FUNDO MUNICIPAL DE JUVENTUDE DE FORTALEZA': 16901,
        'FUNDO MUNICIPAL DE LIMPEZA URBANA': 19901,
        'FUNDO MUNICIPAL DE POLITICAS SOBRE DROGAS': 11902,
        'FUNDO MUNICIPAL DE SAUDE': 25901,
        'FUNDO MUNICIPAL DE SAUDE - INFRAESTRUTURA': 25902,
        'FUNDO MUNICIPAL DE SEGURANCA CIDADA': 17901,
        'FUNDO MUNICIPAL DOS DIREITOS HUMANOS DA PESSOA IDOSA': 31903,
        'FUNDO MUNICIPAL PARA PROTECAO DOS DIREITOS DA PESSOA COM DEFICIENCIA': 31904,
        'FUNDO PREVIDENCIARIO PREVIFOR/PRE': 18204,
        'GABINETE DO PREFEITO': 11101,
        'GABINETE DO VICE-PREFEITO': 12101,
        'GUARDA MUNICIPAL DE FORTALEZA': 17102,
        'HOSPITAL DISTRITAL MARIA JOSE BARROSO DE OLIVEIRA': 25911,
        'HOSPITAL DISTRITAL EDMILSON BARROS DE OLIVEIRA': 25916,
        'HOSPITAL DISTRITAL EVANDRO AYRES DE MOURA': 25910,
        'HOSPITAL DISTRITAL GONZAGA MOTA/BARRA DO CEARA': 25908,
        'HOSPITAL DISTRITAL GONZAGA MOTA/JOSE WALTER': 25913,
        'HOSPITAL DISTRITAL GONZAGA MOTA/MESSEJANA': 25915,
        'HOSPITAL E MATERNIDADE DRA ZILDA ARNS NEUMANN': 25918,
        'INSTITUTO DE PLANEJAMENTO DE FORTALEZA': 11202,
        'INSTITUTO DE PREVIDENCIA DO MUNICIPIO - ASSISTENCIA A SAUDE DOS SERVIDORES DO MUNICIPIO DE FORTALEZA': 18203,
        'INSTITUTO DE PREVIDENCIA DO MUNICIPIO - PREVFOR': 18202,
        'INSTITUTO DR. JOSE FROTA': 25201,
        'INSTITUTO MUNICIPAL DE DESENVOLVIMENTO DE RECURSOS HUMANOS': 18201,
        'PROCURADORIA GERAL DO MUNICIPIO': 13101,
        'RECURSOS SOB A SUPERVISAO DA SECRETARIA MUNICIPAL DAS FINANCAS': 80101,
        'RECURSOS SOB A SUPERVISAO DA SECRETARIA MUNICIPAL DO PLANEJAMENTO, ORCAMENTO E GESTAO': 80102,
        'RESERVA DE CONTINGENCIA': 90101,
        'SECRETARIA MUNICIPAL DA CONSERVACAO E SERVICOS PUBLICOS': 19101,
        'SECRETARIA MUNICIPAL DA CULTURA DE FORTALEZA': 32101,
        'SECRETARIA MUNICIPAL DA EDUCACAO': 24101,
        'SECRETARIA MUNICIPAL DA GESTAO REGIONAL': 33101,
        'SECRETARIA MUNICIPAL DA INFRAESTRUTURA': 27101,
        'SECRETARIA MUNICIPAL DA JUVENTUDE': 16101,
        'SECRETARIA MUNICIPAL DA SAUDE': 25101,
        'SECRETARIA MUNICIPAL DA SEGURANCA CIDADA': 17101,
        'SECRETARIA MUNICIPAL DAS FINANCAS': 23101,
        'SECRETARIA MUNICIPAL DE GOVERNO': 15101,
        'SECRETARIA MUNICIPAL DO DESENVOLVIMENTO ECONOMICO': 26101,
        'SECRETARIA MUNICIPAL DO DESENVOLVIMENTO HABITACIONAL DE FORTALEZA': 34101,
        'SECRETARIA MUNICIPAL DO ESPORTE E LAZER': 29101,
        'SECRETARIA MUNICIPAL DO PLANEJAMENTO, ORCAMENTO E GESTAO': 18101,
        'SECRETARIA MUNICIPAL DO TURISMO DE FORTALEZA': 30101,
        'SECRETARIA MUNICIPAL DO URBANISMO E MEIO AMBIENTE': 28101,
        'SECRETARIA MUNICIPAL DOS DIREITOS HUMANOS E DESENVOLVIMENTO SOCIAL': 31101,
    }

    if orgao in orgao_dict:
        orgao = orgao_dict[orgao]
    else:
        return JSONResponse(
            status_code=status.HTTP_513_REQUEST_HEADER_FIELDS_TOO_LARGE,
            content={"code": 513, "message": "Argumentos invalidos", 
                     "datetime": datetime.now().isoformat()}
        )
    
    logger.info(f"Consulta: {ano_exercicio} - {orgao}")
    
    # Configura os timeouts
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    session = aiohttp.ClientSession(timeout=timeout)
    
    # Configurando headers
    session.headers.update(get_headers())
    
    session.headers.update({'Referer': 'https://portaltransparencia.fortaleza.ce.gov.br'})
    
     # Fazendo a consulta
    try:
        url = f'https://portaltransparencia-back.sepog.fortaleza.ce.gov.br/api/convenios/{ano_exercicio}?orgao={orgao}'
        async with session.get(url, ssl=False, allow_redirects=True) as resp:
            logger.debug(f"Consulta: {resp.status} - {url}")
            response_data = await resp.json()

            if not response_data:
                result = ResponseDefault(
                    code=0,
                    message='Convênio não encontrado.',
                    results=[],
                    datetime=str(datetime.now()),
                )
            else:
                results = [ResponseSite(**item) for item in response_data]  # Cria uma lista de ResponseSite
                result = ResponseDefault(
                    code=0,
                    message='Convênios encontrados.',
                    results=results,
                    datetime=str(datetime.now()),
                )
    except Exception as e:
        logger.exception('Erro durante a consulta API')
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'code': 500,
                'message': f'INTERNAL_SERVER_ERROR: {str(e)}'
            }
        )
    else:
        logger.info(f"Consulta finalizada: {result}")
        await session.close()
        return result