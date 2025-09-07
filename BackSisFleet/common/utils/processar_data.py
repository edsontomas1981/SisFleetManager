from datetime import date, datetime  # Importação necessária

def processar_datas(dados, campos_data):
    """
    Processa campos de data string para objetos date
    
    Args:
        dados (dict): Dicionário com os dados a serem processados
        campos_data (list): Lista de nomes de campos que são datas
    
    Returns:
        tuple: (dados_processados, erro) ou (dados, None) se sucesso
    """
    dados = dados.copy()  # Não modifica o original
    
    for campo in campos_data:
        if campo in dados and dados[campo]:
            # Se já é objeto date, não precisa converter
            if isinstance(dados[campo], (date, datetime)):
                if isinstance(dados[campo], datetime):
                    dados[campo] = dados[campo].date()
                continue
                
            # Tenta converter string para date
            try:
                dados[campo] = datetime.strptime(str(dados[campo]), "%Y-%m-%d").date()
            except ValueError:
                return None, f"Formato inválido para {campo}. Use YYYY-MM-DD."
    
    return dados, None
