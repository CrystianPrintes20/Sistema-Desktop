from ctypes.wintypes import PINT
import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime

url = "https://minhavidaacademica.ufopa.edu.br:5000/api.paem"
#url = "http://webservicepaem-env.eba-mkyswznu.sa-east-1.elasticbeanstalk.com/api.paem/"


def login(usuario: str = None, senha: str = None):
    resposta = ""
    try:
        autenticacao = HTTPBasicAuth(usuario, senha)
        print(autenticacao)
        response = requests.post(url + "/auth", auth=autenticacao)
        print(response)
        res = str(response)[10:15]
        token = ""
        if res == "[200]":
            token = json.loads(response.content).get("token")
            header= {"Authorization": f"Bearer {token}"}
            resp = requests.get(url + "/usuarios/usuario", headers=header)
            re = resp.json()
            tipo = re['tipo']
            print(tipo)
            resposta = True
            return token, resposta, tipo
        elif res == "[401]":
            resposta = False
            return "", resposta, ""

    except:
        resposta = "Falha de conexão\nVerifique a conexão com a internet"
        return "", resposta, ""

def verificar_cadastro(token: str = None, n_matricula: str = None):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            #"Content-Type": "application/json",
        }
        res = requests.get(url + "/discentes", headers=headers)
        lista = res.json()
        #print(lista)
        n_matricula = str(n_matricula)

        verifica_matricula = False

        for i in lista:
            if n_matricula in i.values():
                nome_discente = i['nome']
                id_discente = i['id']
                verifica_matricula = True
                return verifica_matricula, nome_discente, id_discente
                
        return verifica_matricula, '', '' 
    except:
        return "", "", "", "", "Ocorreu erro de conexão.\n Verifique sua internet"

def solicita_dados(token: str = None, n_matricula: str = None, id_discente: str = None):
    try:
        
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(
            url + f"/solicitacoes_acessos?discente_id_discente={id_discente}", headers=headers
        )
        #res = requests.get(url + "/solicitacoes_acessos", headers=headers)
        lista = res.json()
        """ print('########')
        print(lista)
        print('########') """
        data = ""
        verificacao = ""
        data_atual = datetime.today().strftime('%Y-%m-%d')

        for i in lista:
            #Busca as solicitações que sejam do dia atual
            if data_atual in i.values():
            
                verificacao = True
                data = i

        if len(data) == 0:
            verificacao = False
            return "", "", "", "", verificacao

        elif verificacao is True:
            id_solicitacao = data["id"]
            area_solicitada = data["recurso_campus"]
            dados = dict()
            dados["nome_aluno"] = data["discente"]
            dados["matricula"] = data["matricula"]
            dados["para_si"] = data["para_si"]
            dados["data_solicitacao"] = data["data"]
            dados["campus_instituto_id_campus_instituto"] = data[
                "campus_instituto_id_campus_instituto"
            ]
            dados["recurso_campus_id_recurso_campus"] = data[
                "recurso_campus_id_recurso_campus"
            ]
            dados["hora_ini"] = data["hora_inicio"]
            dados["hora_fim"] = data["hora_fim"]
            dados["status_acesso"] = data["status_acesso"]
            dados['acesso_permitido'] = data['acesso_permitido']
            tipo_restricao = data["tipo_restricao"]
            return dados, id_solicitacao, area_solicitada, tipo_restricao, verificacao
    except:
        return "", "", "", "", "Ocorreu erro de conexão.\n Verifique sua internet"


def enviar_dados(token: str = None, n_matricula: str = None, dicio: object = None, id_discente: str = None):
    entrada = dicio["entrada"]
    saida = dicio["saida"]
    temperatura = dicio["temperatura"]

    error = ""
    dt, id_solicitacao, _, _, _ = solicita_dados(token, n_matricula, id_discente)
    id_campus = dt["campus_instituto_id_campus_instituto"]
    id_recurso = (dt["recurso_campus_id_recurso_campus"],)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.get(url + "/acessos_permitidos", headers=headers)
        error = "Dados enviados\n com sucesso"
    except:
        error = "Falha ao enviar dados"
    lista = r.json()
    id_acesso = lista[len(lista) - 1]["id_acesso_permitido"]
    id_acesso += 1
    dict_dados = {
        "hora_entrada": entrada,
        "hora_saida": saida,
        "matricula_discente": n_matricula,
        "temperatura": temperatura,
        "solicitacao_acesso_id_solicitacao_acesso": id_solicitacao,
        "recurso_campus_id_recurso_campus": id_recurso,
        "campus_instituto_id_campus_instituto": id_campus,
    }
    try:
        r = requests.post(
            url + "/acessos_permitidos/acesso_permitido",
            data=json.dumps(dict_dados),
            headers=headers,
        )
        error = "Dados enviados\n com sucesso"
    except:
        error = "Falha ao enviar dados"

    return error


def ponto(matricula: str = None, token: str = None, id_discente: str = None):
    error = ""
    try:
        dados, id_solicitacao, _, _, _ = solicita_dados(token, matricula, id_discente)
        nome_usuario = dados["nome_aluno"]
        print('verificacão ponto')
        print(dados)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        error = True
        r = requests.get(url + "/acessos_permitidos", headers=headers)
        lista = r.json()

        id_acesso_permitido = ""
        hora_saida = ""

        for solicitacao in lista:
            if id_solicitacao in solicitacao.values():
                id_acesso_permitido = solicitacao["id_acesso_permitido"]
                hora_saida = solicitacao["hora_saida"]
        error = True

        if hora_saida == "00:00:00":
            hd = datetime.now()
            horario_atual = hd.strftime("%H:%M:%S")
            dict_dados = {
                "id_acesso_permitido": id_acesso_permitido,
                "hora_saida": horario_atual,
            }
            r = requests.put(
                url + "/acessos_permitidos/acesso_permitido",
                data=json.dumps(dict_dados),
                headers=headers,
            )
            error = True
            return error, nome_usuario, horario_atual
        else:
            error = False
            return error, " ", " "
    except:
        error = "Erro na busca do registro.\nContatar o técnico"
        return error, " ", " "


def verifica_vacinacao(token: str = None, matricula: str = None):
    error = ""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(
            url + f"/discente_vacinacao?matricula={matricula}", headers=headers
        )
        lista = r.json()
        quantidade = lista["quantidade_vacinas"]
        fabricante = lista["fabricante"].lower()
        carteirinha = lista['carteirinha_vacinacao']
        error = True
        return quantidade, fabricante, error, carteirinha
    except:
        error = "Falha ao verificar\nas vacinas."
        return "", "", error

def busca_dados_userlogado(token: str = None):
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            #"Content-Type": "application/json",
        }
        res = requests.get(url + "/usuarios/usuario", headers=headers)
        dados_userlogado = res.json()
        #print(dados_userlogado)
        campus_instituto_id = dados_userlogado['campus_instituto_id_campus_instituto']
        usuario_id = dados_userlogado['id_usuario']

        respota_busca, id_recurso = busca_recursos(token, campus_instituto_id)
        #print(respota_busca, id_recurso)
        erro = False
        if respota_busca is True:
           return erro, id_recurso, usuario_id
        else:
            #erro = "Erro ao pegar o id recurso"
            return erro, '', ''
    except:
        return "", "", "", "", "Ocorreu erro de conexão.\n Verifique sua internet"

def busca_recursos(token: str = None, id_campus_instituto: str = None):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(
            url + f"/recursos_campus?campus_instituto_id_campus_instituto={id_campus_instituto}", headers=headers
        )
        recursos = r.json()
        nome_campus = ''
        resposta = False

        if len(recursos) == 0:
            return resposta
        else:
            res = requests.get(
                url + f"/campus_institutos/campus_instituto?id_campus_instituto={id_campus_instituto}", headers=headers
            )
            campus = res.json()
            if len(campus) == 0:
               return resposta
            else:
                nome_campus = campus['nome']

        for i in recursos:
            if nome_campus in i.values():
                resposta = True
                id_recurso = i['id']
                return resposta, id_recurso

        return resposta

    except:
        return "", "", "", "", "Ocorreu erro de conexão.\n Verifique sua internet"
        
def envia_reserva(token, recurso_id, data_hoje, hora_ini_hoje, hora_final_hoje, nome_discente, usuario_id, id_discente):
    dados_reserva = {
        "recurso_campus_id_recurso_campus": recurso_id,
        "data": data_hoje,
        "hora_inicio": hora_ini_hoje,
        "hora_fim": hora_final_hoje,
        "nome": nome_discente,
        "usuario_id_usuario": usuario_id,
        "discente_id_discente": id_discente,
        "para_si" : -1,
        "status_acesso" : 1
    }
    print(dados_reserva)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(
            url + "/solicitacoes_acessos/solicitacao_acesso",
            data=json.dumps(dados_reserva),
            headers=headers,
        )
        error = "Reserva feita\n com sucesso!!"
    except:
        error = "Falha ao fazer reserva"
    return error