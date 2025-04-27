import unicodedata
import re

def check_cpf(cpf : str):
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11: return False
    for i in range(9, 11):
        val = sum(int(cpf[j]) * (i + 1 - j) for j in range(i))
        if int(cpf[i]) != (val * 10 % 11) % 10: return False
    return True

def normalize_text(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').lower()

def state_to_uf(state):
    states_uf = {
        'amapa': 'AP',
        'acre': 'AC',
        'alagoas': 'AL',
        'amazonas': 'AM',
        'bahia': 'BA',
        'ceara': 'CE',
        'distrito federal': 'DF',
        'espirito santo': 'ES',
        'goias': 'GO',
        'maranhao': 'MA',
        'mato grosso': 'MT',
        'mato grosso do sul': 'MS',
        'minas gerais': 'MG',
        'para': 'PA',
        'paraiba': 'PB',
        'parana': 'PR',
        'pernambuco': 'PE',
        'piaui': 'PI',
        'rio de janeiro': 'RJ',
        'rio grande do norte': 'RN',
        'rio grande do sul': 'RS',
        'rondonia': 'RO',
        'roraima': 'RR',
        'santa catarina': 'SC',
        'sao paulo': 'SP',
        'sergipe': 'SE',
        'tocantins': 'TO'
    }
    
    state = normalize_text(state.strip())

    if state not in states_uf:
        raise ValueError(f"UF not found for state: {state.capitalize()}")
    
    return states_uf[state]