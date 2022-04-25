from numpy import False_
from sqlalchemy import false
from pyzbar import pyzbar
import cv2
from conexao import solicita_dados, verificar_cadastro, busca_dados_userlogado, envia_reserva
from datetime import datetime, date, timedelta
from PyQt5.QtCore import QEventLoop, QTimer

token = ""


def Token(passe):
    global token
    token = passe


matricula = ""


def Matricula(n_matricula):
    global matricula
    matricula = n_matricula
    return matricula

id_discente = ""


def Discente_id(discente_id):
    global id_discente
    id_discente = discente_id
    return id_discente

dados = ""


def Dados(data):
    global dados
    dados = data


"""tipo = ""


def Tipo(tipo_user):
    global tipo
    tipo = tipo_user"""


def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    barcode_info = ""
    ok = ""
    for barcode in barcodes:
        x, y, w, h = barcode.rect
        # 1
        barcode_info = barcode.data.decode("utf-8")
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
        # 2
        with open("barcode_result.txt", mode="w") as file:
            file.write(barcode_info)
        ok = True
    return frame, ok


def dados_aluno():
    print("entrou aqui")
    with open("barcode_result.txt", mode="r") as file:
        dado = file.readlines()
    
    dados_qr = dado[0]
    dados_qr = dados_qr.split(";")

    if len(dados_qr) < 3:
        qr_code = False
        return "", "", "", "", "", "", "", "", "", "", "" ,qr_code, ""   
    else:
        n_matricula = dados_qr[0]
        curso = dados_qr[2]
        Matricula(n_matricula)
        permissao = ""

    res_veri_matricula, nome_discente, id_discente= verificar_cadastro(token, n_matricula)
    
    if res_veri_matricula is True:
        Discente_id(id_discente)
        HD = datetime.now()
        datas, _, area_solicitada, tipo_restricao, verificacao = solicita_dados(
            token, n_matricula, id_discente
        )

        Dados(datas)
        if verificacao is False:
            print("False")
            return "", "", "", "", "", "", "", "", "", "", verificacao, "", ""
        elif verificacao is True:
            nome_aluno = dados["nome_aluno"]
            data_solicitacao = dados["data_solicitacao"]
            hora_ini = dados["hora_ini"]
            hora_fim = dados["hora_fim"]
            status_acesso = dados["status_acesso"]
            if status_acesso == -1:
                permissao = "Negado"
            else:
                permissao = "Permitido"

            data_solicitacao = data_solicitacao.split("-")
            data_solicitacao = "{}/{}/{}".format(
                data_solicitacao[2], data_solicitacao[1], data_solicitacao[0]
            )

            hora_inicial = hora_ini.split(":")
            hora_final = hora_fim.split(":")

            hora_solicitada_ini = HD.replace(
                hour=int(hora_inicial[0]),
                minute=int(hora_inicial[1]),
                second=int(hora_inicial[2]),
            )
            hora_solicitada_fim = HD.replace(
                hour=int(hora_final[0]),
                minute=int(hora_final[1]),
                second=int(hora_final[2]),
            )
            return (
                tipo_restricao,
                nome_aluno,
                permissao,
                data_solicitacao,
                hora_solicitada_fim,
                hora_solicitada_ini,
                area_solicitada,
                curso,
                hora_ini,
                hora_fim,
                verificacao,
                "",
                ""
            )
    else:
        return "", "", "", "", "", "", "", "", "", "", "" , "", res_veri_matricula 

def resevar_recursos():

    HD = datetime.now()

    data_hoje = HD.strftime("%Y-%m-%d")
    hora_ini_hoje = HD.strftime("%H:%M:%S")
    hora_fim_hoje = HD + timedelta(hours=2)
    hora_final_hoje = hora_fim_hoje.strftime("%H:%M:%S")

    verificacao, recurso_id, usuario_id = busca_dados_userlogado(token)
    #print(verificacao, recurso_id, usuario_id)
    retorno_envia_reserva = False

    if verificacao is False:
        retorno_envia_reserva = True

        res_veri_matricula, nome_discente, id_discente = verificar_cadastro(token, matricula)
        #print(res_veri_matricula, nome_discente, id_discente)
        resposta_envia = envia_reserva(token,recurso_id, data_hoje, hora_ini_hoje, hora_final_hoje, nome_discente, usuario_id, id_discente)
        
        return retorno_envia_reserva, resposta_envia

    elif verificacao is True:
        
        return retorno_envia_reserva, ''

def sleep(segundos):
    mili = segundos * 1000
    loop = QEventLoop()
    QTimer.singleShot(mili, loop.quit)
    loop.exec_()
