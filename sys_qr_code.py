from msilib import CAB
import os
from re import template
import cv2
from PyQt5 import QtCore
from pymysql import NULL
from sqlalchemy import null
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from _imagens import imagens
from conexao import enviar_dados, ponto, verifica_vacinacao
from datetime import datetime, date, timedelta
from util import read_barcodes, dados_aluno, sleep, resevar_recursos
import util
from MVA import confirma
from PyQt5.QtCore import Qt
from detalhes_ui import detalhes, normal, displayImage
# Import only b64decode function from the base64 module
from base64 import b64decode
#from PyQt5 import QtWebEngineWidgets


USER = ""
HORARIO_ATUAL = ""
HD = ""
DATA = ""
CART = 0

class sis_qr_code(QMainWindow):
    global HORARIO_ATUAL, HD, USER, DATA, CART
    HD = datetime.now()
    HORARIO_ATUAL = HD.strftime("%H:%M:%S")
    today = date.today()
    DATA = today.strftime("%d/%m/%Y")

    def __init__(self):

        super(sis_qr_code, self).__init__()
        self.window = loadUi("leitor_qr2.ui", self)
        self.logic = 0
        self.cart_vac = 0
        print('primeiro logic', self.logic)
        print('primeiro cart_vac ', self.cart_vac)
        self.value = 0
        # BOTÃO QUE ABRE A CÂMERA
        self.abrir_camera.clicked.connect(self.onClicked)
        # BOTÃO QUE FECHA A CÂMERA
        self.fechar_camera.clicked.connect(self.CloseCapture)
        # BOTÃO QUE HABILITA A CARTEIRINHA
        self.habilita_carteinha.clicked.connect(self.habilitar_carteirinha)
        # BOTÃO QUE DESABILITA A CARTEIRINHA
        #self.desabilita_carteinha.clicked.connect(self.desabilitar_carteinha)
        # BOTÃO DE LOGOUT
        self.sair.clicked.connect(self.closeEvent)
        # BOTÃO DE AUTORIZAR
        self.afirmar.clicked.connect(self.autorizar)
        # BOTÃO DE NÃO AUTORIZAR
        self.negar.clicked.connect(self.nao_autorizar)
        # BOTÃO DE ENVIAR TEMPERATURA
        self.enviar_temp.clicked.connect(self.salvar_temp)
        self.confirmar.clicked.connect(self.permitir)
        # BOTÕES DE ENVIAR OU NAO TEMPERATURA
        self.sim.clicked.connect(self.opcao_sim)
        self.nao.clicked.connect(self.opcao_nao)
        #botão de proximo frame
        self.proximo.clicked.connect(self.seguinte)

        self.abrir_camera.setShortcut(QKeySequence("Ctrl+C"))
        self.fechar_camera.setShortcut(QKeySequence("Ctrl+C"))
        self.sair.setShortcut(QKeySequence("Ctrl+S"))
        self.sim.setShortcut(QKeySequence("Enter"))
        self.afirmar.setShortcut(QKeySequence("Enter"))
        self.proximo.setShortcut(QKeySequence("Enter"))
        self.enviar_temp.setShortcut(QKeySequence("Enter"))
        self.negar.setShortcut(QKeySequence("Delete"))
        self.nao.setShortcut(QKeySequence("Delete"))

        # CONTROLE DE CAMADAS
        self.window.mostrar_carteirinha.close()
        self.window.habilita_carteinha.close()
        self.window.desabilita_carteinha.close()
        self.window.temp.close()
        self.window.aviso_temp.close()
        self.window.fechar_camera.close()
        self.window.observacao.close()
        self.window.regi_saida.close()
        self.window.frame_user.show()
        self.window.campus_all.close()
        self.window.fechar_confirma.close()
        self.window.fechar_negar.close()
        self.window.campus_restricao.close()
        self.window.proximo.close()
        self.label_user.setText(f"Usuário {USER}")
        self.label_user.setStyleSheet(
            "color: rgb(255, 255, 255);\n"
            'font: 75 16pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;\n"
            "align: center;"

        )


    @pyqtSlot()
    def onClicked(self):
        self.window.abrir_camera.close()
        self.window.fechar_camera.show()
        self.window.observacao.close()
        self.window.habilita_carteinha.close()
        self.window.proximo.close()
        # FUNÇÃO QUE ABRE A CÂMERA
        self.window.imgLabel.show()
        try:
            self.cap = cv2.VideoCapture(0)
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                ok = False
                frame, ok = read_barcodes(frame)
                displayImage(self.window, frame, 1)
                cv2.waitKey(0)
                
                if ok is True:
                   
                    (
                        abertura,
                        nome_aluno,
                        permissao,
                        data_solicitacao,
                        hora_comparacao_fim,
                        hora_comparacao_ini,
                        area,
                        curso,
                        hora_ini,
                        hora_fim,
                        verificacao,
                        veri_qrcode,
                        veri_matricula
                    ) = dados_aluno()

                    self.window.regi_saida.show()
                    self.window.proximo.close()
                    self.text_saida.setText("Verificando dados...")
                    self.regi_saida.setStyleSheet(
                        "background-color: rgb(73, 122, 166);\n"
                        "color: rgb(255, 255, 255);\n"
                        'font: 75 18pt "Arial";\n'
                        "padding-top:5px;\n"
                        "padding-left: 5px;\n"
                        "align: center;"
                    )
                    self.text_saida.setStyleSheet(
                        "background-color: rgb(73, 122, 166);\n"
                        "color: rgb(255, 255, 255);\n"
                        'font: 75 18pt "Arial";\n'
                        "padding-top:5px;\n"
                        "padding-left: 5px;\n"
                        "align: center;"
                    )
                    sleep(1)
                    """print(dados_aluno())
                    print(verificacao)"""

                    # Verifica se o qr_code é valido
                    if veri_qrcode is False:
                        #Qr_code invalido
                        self.window.regi_saida.show()
                        self.text_saida.setText("Qr_code\ninvalido!!")
                        self.regi_saida.setStyleSheet(
                            'padding: 25px;\n'
                            'border-radius: 3px\n;'
                            "background-color: #f00;\n"
                            "border-color: #e8273b;\n"
                            "color: #FFF;\n"
                            'font: 75 18pt "Arial";\n'
                            "padding-top:5px;\n"
                            "padding-left: 5px;\n"
                            "align: center;"	
                        )
                        self.text_saida.setStyleSheet(
                            'padding: 25px;\n'
                            'border-radius: 3px\n;'
                            "background-color: #f00;\n"
                            "border-color: #e8273b;\n"
                            "color: #FFF;\n"
                            'font: 75 18pt "Arial";\n'
                            "padding-top:5px;\n"
                            "padding-left: 5px;\n"
                            "align: center;"
                        )	
                        sleep(5)
                        self.window.regi_saida.close()
                        self.window.CAPA.show()
                    else:
                        #Qr_code VALIDO
                        # Verifica de o usuario está cadastrado no sistema
                        if veri_matricula is False:
                            #Usuario NÃO cadastrado
                            self.window.regi_saida.show()
                            self.text_saida.setText(
                                "Usuario não cadastrado\n no sistema\n Minha Vida Academica"
                            )
                            self.text_saida.setStyleSheet(
                                "background-color: rgb(73, 122, 166);\n"
                                "color: rgb(255, 255, 255);\n"
                                'font: 75 16pt "Arial";\n'
                                "padding-top:5px;\n"
                                "padding-left: 5px;\n"
                                "align: center;"
                            )
                            sleep(5)
                            self.window.regi_saida.close()
                            self.window.CAPA.show()
                           
                        else:
                            #Usuario cadastrado
                            if verificacao is False:

                                self.window.regi_saida.show()
                     
                                self.text_saida.setText("Aluno sem reserva\n nesse horario.\n criando reserva...")
                                self.regi_saida.setStyleSheet(
                                    'padding: 25px;\n'
                                    'border-radius: 3px\n;'
                                    "background-color: #C27400;\n"
                                    "border-color: #f4a911;\n"
                                    "color: #FFF;\n"
                                    'font: 75 18pt "Arial";\n'
                                    "padding-top:5px;\n"
                                    "padding-left: 5px;\n"
                                    "align: center;"	
                                )
                                self.text_saida.setStyleSheet(
                                    'padding: 25px;\n'
                                    'border-radius: 3px\n;'
                                    "background-color: #C27400;\n"
                                    "border-color: #f4a911;\n"
                                    "color: #FFF;\n"
                                    'font: 75 18pt "Arial";\n'
                                    "padding-top:5px;\n"
                                    "padding-left: 5px;\n"
                                    "align: center;"	
                                )
                                resposta_retorno, retorno_reserva = resevar_recursos()
                                sleep(7)

                                #fazer a verificação da resposta_retorno
                                if resposta_retorno == True:

                                    print(retorno_reserva)
                                    self.window.regi_saida.show()
                                    self.window.proximo.show() 
                                    self.text_saida.setText(retorno_reserva)
                                    self.regi_saida.setStyleSheet(
                                        'padding: 25px;\n'
                                        'border-radius: 3px\n;'
                                        "background-color: #299969;\n"
                                        "border-color: #f4a911;\n"
                                        "color: #FFF;\n"
                                        'font: 75 18pt "Arial";\n'
                                        "padding-top:5px;\n"
                                        "padding-left: 5px;\n"
                                        "align: center;"	
                                    )
                                    self.text_saida.setStyleSheet(
                                        'padding: 25px;\n'
                                        'border-radius: 3px\n;'
                                        "background-color: #299969;\n"
                                        "border-color: #f4a911;\n"
                                        "color: #FFF;\n"
                                        'font: 75 18pt "Arial";\n'
                                        "padding-top:5px;\n"
                                        "padding-left: 5px;\n"
                                        "align: center;"	
                                    )
                                    sleep(5)

                                else:
                                    self.window.regi_saida.show()
                                    self.text_saida.setText("Falha ao criar reserva")
                                    self.regi_saida.setStyleSheet(
                                            'padding: 25px;\n'
                                            'border-radius: 3px\n;'
                                            "background-color: #f00;\n"
                                            "border-color: #e8273b;\n"
                                            "color: #FFF;\n"
                                            'font: 75 18pt "Arial";\n'
                                            "padding-top:5px;\n"
                                            "padding-left: 5px;\n"
                                            "align: center;"	
                                        )
                                    self.text_saida.setStyleSheet(
                                            'padding: 25px;\n'
                                            'border-radius: 3px\n;'
                                            "background-color: #f00;\n"
                                            "border-color: #e8273b;\n"
                                            "color: #FFF;\n"
                                            'font: 75 18pt "Arial";\n'
                                            "padding-top:5px;\n"
                                            "padding-left: 5px;\n"
                                            "align: center;"	
                                    )

                            elif verificacao is True:
                                resposta,nome, h_saida = ponto(util.matricula, util.token, util.id_discente)
                                quantidade, fabricante, error, carteirinha = verifica_vacinacao(
                                    util.token, util.matricula
                                )
                                print('resposta: ', resposta)
                                #print(quantidade, fabricante, error, carteirinha)

                                if error is True:
                                    print(error)
                                    pass
                                else:
                                    self.window.regi_saida.show()
                                    self.text_saida.setText(error)
                                    self.text_saida.setStyleSheet(
                                        "background-color: rgb(73, 122, 166);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        'font: 75 14pt "Arial";\n'
                                        "padding-top:5px;\n"
                                        "padding-left: 5px;\n"
                                        "align: center;"
                                    )
                                    sleep(3)
                                    self.cap.release()
                                    self.window.imgLabel.close()
                                    self.window.fechar_camera.close()
                                    self.window.abrir_camera.show()
                                    self.logic = 0
                                    print("segundo logic", self.logic)
                                    self.window.CAPA.show()

                                if resposta is False:
                                    print('Entrou na resposta')
                                    if abertura == 1 or abertura == 2:
                                        print ('abertura 1 ou 2')
                                        self.window.regi_saida.close()
                                        self.window.CAPA.close()
                                        self.window.campus_restricao.close()
                                        self.window.campus_all.show()

                                        #subtrair 2 horas da data atual
                                        hora_inicio_com = hora_comparacao_ini - timedelta(hours=2)
                                        print(hora_inicio_com)
                                        #soma 2 horas da data atual
                                        hora_fim_com = hora_comparacao_fim + timedelta(hours=2)
                                        print(hora_fim_com)

                                        """  time_1 = datetime.strptime(hora_inicio_com, "%H:%M:%S")
                                        time_2 = datetime.strptime(hora_fim_com, "%H:%M:%S")
                                        time_3 = datetime.strptime('02:00:00', "%H:%M:%S")

                                        time_hora_incio = (time_1 - time_3)
                                        time_hora_fim = (time_2 + time_3) """
                                                        
                                        if (HD < hora_inicio_com or HD > hora_fim_com):
                                            permissao = "Negado"
                                        
                                        elif quantidade <= 3:

                                            if (
                                                quantidade == 1
                                                and fabricante.lower() == "janssen_j&j"
                                            ):
                                                permissao = "Permitido"
                                            elif (quantidade == 2 or quantidade == 3):
                                                permissao = "Permitido"
                                            elif (
                                                quantidade == 1
                                                and fabricante.lower() != "janssen_j&j"
                                            ) or (quantidade == 0):
                                                permissao = "Negado"

                                        self.nome_aluno.setText(nome_aluno)
                                        self.matricula.setText("Matricula: %s" % util.matricula)
                                        self.curso.setText("Curso: %s" % curso)
                                        self.espaco_reservado.setText(
                                            "Espaço Reservado: %s" % area
                                        )
                                        self.hora_ini.setText("Inicio: %s" % hora_ini)
                                        self.hora_fim.setText("Fim: %s" % hora_fim)
                                        self.data.setText("Data: %s" % data_solicitacao)

                                        print(permissao)
                                        # DA SINAL VERMELHO CASO O ACESSO SEJA NEGADO
                                        if permissao == "Negado":
                                          
                                            if quantidade < 2:
                                               
                                                detalhes(self.window, "255", "0", "0")
                                                self.window.afirmar.close()
                                                self.window.proximo.close()
                                                self.window.negar.close()
                                                self.observacao.show()
                                                self.observacao.setText(
                                                    "Não tomou as duas doses da vacina\ncontra Covid-19"
                                                )
                                                self.observacao.setStyleSheet(
                                                    "background-color: rgb(255, 0, 0);\n"
                                                    "color: rgb(255, 255, 255);\n"
                                                    'font: 75 14pt "Arial";\n'
                                                    "padding-top:5px;\n"
                                                    "padding-left: 5px;\n"
                                                    "align: center;"
                                                )
                                            else:
                                                normal(self.window)
                                                self.window.campus_all.close()
                                                self.window.CAPA.show()
                                                self.window.regi_saida.show()
                                                self.text_saida.setText("Reserva\n fora do horario.\n Atualizando reserva...")
                                                self.regi_saida.setStyleSheet(
                                                    'padding: 25px;\n'
                                                    'border-radius: 3px\n;'
                                                    "background-color: #f6bb42;\n"
                                                    "border-color: #f4a911;\n"
                                                    "color: #FFF;\n"
                                                    'font: 75 18pt "Arial";\n'
                                                    "padding-top:5px;\n"
                                                    "padding-left: 5px;\n"
                                                    "align: center;"	
                                                )
                                                self.text_saida.setStyleSheet(
                                                    'padding: 25px;\n'
                                                    'border-radius: 3px\n;'
                                                    "background-color: #f6bb42;\n"
                                                    "border-color: #f4a911;\n"
                                                    "color: #FFF;\n"
                                                    'font: 75 18pt "Arial";\n'
                                                    "padding-top:5px;\n"
                                                    "padding-left: 5px;\n"
                                                    "align: center;"	
                                                )
                                                sleep(5)
                                                    
                                                resposta_retorno, retorno_reserva = resevar_recursos()
                                                print("retorno", resposta_retorno)

                                                #fazer a verificação da resposta_retorno
                                                if resposta_retorno == True:

                                                    print(retorno_reserva)
                                                    self.window.regi_saida.show()
                                                    self.window.proximo.show() 
                                                    self.text_saida.setText(retorno_reserva)
                                                    self.regi_saida.setStyleSheet(
                                                        'padding: 25px;\n'
                                                        'border-radius: 3px\n;'
                                                        "background-color: #299969;\n"
                                                        "border-color: #f4a911;\n"
                                                        "color: #FFF;\n"
                                                        'font: 75 18pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"	
                                                    )
                                                    self.text_saida.setStyleSheet(
                                                        'padding: 25px;\n'
                                                        'border-radius: 3px\n;'
                                                        "background-color: #299969;\n"
                                                        "border-color: #f4a911;\n"
                                                        "color: #FFF;\n"
                                                        'font: 75 18pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"	
                                                    )
                                                    sleep(5)

                                                    self.window.regi_saida.close()
                                                    
                                                else:
                                                    self.window.regi_saida.show()
                                                    self.text_saida.setText("Falha ao criar reserva")
                                                    self.regi_saida.setStyleSheet(
                                                        'padding: 25px;\n'
                                                        'border-radius: 3px\n;'
                                                        "background-color: #f00;\n"
                                                        "border-color: #e8273b;\n"
                                                        "color: #FFF;\n"
                                                        'font: 75 18pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"	
                                                    )
                                                    self.text_saida.setStyleSheet(
                                                        'padding: 25px;\n'
                                                        'border-radius: 3px\n;'
                                                        "background-color: #f00;\n"
                                                        "border-color: #e8273b;\n"
                                                        "color: #FFF;\n"
                                                        'font: 75 18pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"	
                                                       'font: 75 16pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"
                                                    )
                                            if quantidade == 0:

                                                self.window.p_dose_all.setStyleSheet(
                                                    "background-color: rgb(157, 157, 157);"
                                                )
                                                self.window.fig_vac_1.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(157, 157, 157);"
                                                )
                                                self.window.p_dose_n.setStyleSheet(
                                                    "background-color: rgb(157, 157, 157);"
                                                )
                                                self.window.s_dose_all.setStyleSheet(
                                                    "background-color: rgb(157, 157, 157);"
                                                )
                                                self.window.fig_vac_2.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(157, 157, 157);"
                                                )
                                                self.window.s_dose_n.setStyleSheet(
                                                    "background-color: rgb(157, 157, 157);"
                                                )

                                            elif ( quantidade == 1 and fabricante.lower() != "janssen_j&j"):
                                                
                                                self.window.p_dose_all.setStyleSheet(
                                                    "background-color: rgb(157, 157, 157);"
                                                )
                                                self.window.fig_vac_1.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(157, 157, 157);"
                                                )
                                                self.window.p_dose_n.setStyleSheet(
                                                    "background-color: rgb(157, 157, 157);"
                                                )

                                            elif quantidade == 2 or quantidade == 3:
                                                self.window.p_dose_all.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.fig_vac_1.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.p_dose_n.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.s_dose_all.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.fig_vac_2.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.s_dose_n.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )

                                            sleep(5)
                                            normal(self.window)
                                            self.window.campus_all.close()
                                            self.window.CAPA.show()

                                        # DA SINAL VERDE CASO O ACESSO SEJA PERMITIDO
                                        elif permissao == "Permitido":
                                            print ('permissão permitida')
                                            ######
                                            self.window.habilita_carteinha.show()
                                            #####
                                            detalhes(self.window, "73", "122", "166")
                                            self.window.afirmar.show()
                                            self.window.negar.show()

                                            if quantidade == 2 or quantidade == 3:
                                                self.window.p_dose_all.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.fig_vac_1.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.p_dose_n.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.s_dose_all.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.fig_vac_2.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.s_dose_n.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                            elif ( quantidade == 1 and fabricante.lower() == "janssen_j&j"):
                                                self.window.p_dose_all.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.fig_vac_1.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.p_dose_n.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )

                                    elif abertura == 0:
                                        print ('abertura 0')
                                        self.window.afirmar.show()
                                        self.window.proximo.close()
                                        self.window.negar.show()
                                        self.window.regi_saida.close()
                                        self.window.CAPA.close()
                                        self.window.campus_all.close()
                                        self.window.campus_restricao.show()

                                        #subtrair 2 horas da data atual
                                        hora_inicio_com = hora_comparacao_ini - timedelta(hours=2)
                                        print(hora_inicio_com)
                                        #soma 2 horas da data atual
                                        hora_fim_com = hora_comparacao_fim + timedelta(hours=2)
                                        print(hora_fim_com)

                                        # data = DATA          
                                        if (HD < hora_inicio_com or HD > hora_fim_com):
                                            permissao = "Negado"
                                            resp_hora = 'Fora_do_horario'
                                        elif quantidade <= 3:
                                            if (quantidade >= 2) or (
                                                quantidade == 1
                                                and fabricante.lower() == "janssen_j&j"
                                            ):
                                                permissao = "Permitido"

                                            elif (
                                                quantidade == 1
                                                and fabricante.lower() != "janssen_j&j"
                                            ) or (quantidade == 0):
                                                permissao = "Negado"

                                        self.nome_aluno_r.setText(nome_aluno)
                                        self.matricula_r.setText(
                                            "Matricula: %s" % util.matricula
                                        )
                                        self.curso_r.setText("Curso: %s" % curso)
                                        self.hora_ini_r.setText("Inicio: %s" % HORARIO_ATUAL)
                                        self.data_r.setText("Data: %s" % data_solicitacao)

                                        # DA SINAL VERMELHO CASO O ACESSO SEJA negado
                                        if permissao == "Negado":
                                            print('permissao negado')
                                            self.window.afirmar.show()
                                            self.window.negar.show()
                                            self.window.confirmar.close()

                                            if(quantidade == 1 or quantidade == 0):
                                                print("entrou aqui na vacina")
                                                self.observacao_r.show()
                                                self.observacao_r.setText(
                                                    "Não tomou as duas doses da vacina\ncontra Covid-19"
                                                )
                                                self.observacao_r.setStyleSheet(
                                                    "background-color: rgb(255, 0, 0);\n"
                                                    "color: rgb(255, 255, 255);\n"
                                                    'font: 75 14pt "Arial";\n'
                                                    "padding-top:5px;\n"
                                                    "padding-left: 5px;\n"
                                                    "align: center;"
                                                )
                                                detalhes(self.window, "255", "0", "0")

                                                if quantidade == 0:
                                                    self.window.p_dose.setStyleSheet(
                                                        "background-color: rgb(157, 157, 157);"
                                                    )
                                                    self.window.fig_vac_r.setStyleSheet(
                                                        "image: url(:/newPrefix/2646111.png);\n"
                                                        "background-color: rgb(157, 157, 157);"
                                                    )
                                                    self.window.p_dose_n_r.setStyleSheet(
                                                        "background-color: rgb(157, 157, 157);"
                                                    )
                                                    self.window.s_dose.setStyleSheet(
                                                        "background-color: rgb(157, 157, 157);"
                                                    )
                                                    self.window.fig_vac_r_2.setStyleSheet(
                                                        "image: url(:/newPrefix/2646111.png);\n"
                                                        "background-color: rgb(157, 157, 157);"
                                                    )
                                                    self.window.s_dose_n_r.setStyleSheet(
                                                        "background-color: rgb(157, 157, 157);"
                                                    )

                                                elif (quantidade == 1 and fabricante.lower() != "janssen_j&j"):
                                                    self.window.p_dose.setStyleSheet(
                                                        "background-color: rgb(157, 157, 157);"
                                                    )
                                                    self.window.fig_vac_r.setStyleSheet(
                                                        "image: url(:/newPrefix/2646111.png);\n"
                                                        "background-color: rgb(157, 157, 157);"
                                                    )
                                                    self.window.p_dose_n_r.setStyleSheet(
                                                        "background-color: rgb(157, 157, 157);"
                                                    )

                                            elif resp_hora == 'Fora_do_horario':
                                                print("xczczczxczxczx")
                                                normal(self.window)
                                                self.window.campus_all.close()
                                                self.window.CAPA.show()
                                                self.window.regi_saida.show()
                                                self.text_saida.setText("Aluno\n fora do horario reservado!\n Atualizando reserva...")
                                                self.regi_saida.setStyleSheet(
                                                    'padding: 25px;\n'
                                                    'border-radius: 3px\n;'
                                                    "background-color: #f6bb42;\n"
                                                    "border-color: #f4a911;\n"
                                                    "color: #FFF;\n"
                                                    'font: 75 18pt "Arial";\n'
                                                    "padding-top:5px;\n"
                                                    "padding-left: 5px;\n"
                                                    "align: center;"	
                                                )
                                                self.text_saida.setStyleSheet(
                                                    'padding: 25px;\n'
                                                    'border-radius: 3px\n;'
                                                    "background-color: #f6bb42;\n"
                                                    "border-color: #f4a911;\n"
                                                    "color: #FFF;\n"
                                                    'font: 75 18pt "Arial";\n'
                                                    "padding-top:5px;\n"
                                                    "padding-left: 5px;\n"
                                                    "align: center;"	
                                                )
                                                sleep(5)
                                                    
                                                resposta_retorno, retorno_reserva = resevar_recursos()
                                                print("retorno", resposta_retorno)

                                                #fazer a verificação da resposta_retorno
                                                if resposta_retorno == True:

                                                    print(retorno_reserva)
                                                    self.window.regi_saida.show()
                                                    self.window.proximo.show() 
                                                    self.text_saida.setText(retorno_reserva)
                                                    self.regi_saida.setStyleSheet(
                                                        'padding: 25px;\n'
                                                        'border-radius: 3px\n;'
                                                        "background-color: #299969;\n"
                                                        "border-color: #f4a911;\n"
                                                        "color: #FFF;\n"
                                                        'font: 75 18pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"	
                                                    )
                                                    self.text_saida.setStyleSheet(
                                                        'padding: 25px;\n'
                                                        'border-radius: 3px\n;'
                                                        "background-color: #299969;\n"
                                                        "border-color: #f4a911;\n"
                                                        "color: #FFF;\n"
                                                        'font: 75 18pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"	
                                                    )
                                                    sleep(5)
                                                    
                                                else:
                                                    self.window.regi_saida.show()
                                                    self.text_saida.setText("Falha ao criar reserva")
                                                    self.regi_saida.setStyleSheet(
                                                        'padding: 25px;\n'
                                                        'border-radius: 3px\n;'
                                                        "background-color: #f00;\n"
                                                        "border-color: #e8273b;\n"
                                                        "color: #FFF;\n"
                                                        'font: 75 18pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"	
                                                    )
                                                    self.text_saida.setStyleSheet(
                                                        'padding: 25px;\n'
                                                        'border-radius: 3px\n;'
                                                        "background-color: #f00;\n"
                                                        "border-color: #e8273b;\n"
                                                        "color: #FFF;\n"
                                                        'font: 75 18pt "Arial";\n'
                                                        "padding-top:5px;\n"
                                                        "padding-left: 5px;\n"
                                                        "align: center;"	
                                                    )

                                            
                                            print('ssddsadsad')
                                            sleep(5)
                                            normal(self.window)
                                            self.window.campus_restricao.close()
                                            self.window.CAPA.show()

                                        # DA SINAL VERDE CASO O ACESSO SEJA PERMITIDO
                                        elif permissao == "Permitido":

                                            print('permissao permitido')
                                            self.window.habilita_carteinha.show()

                                            detalhes(self.window, "73", "122", "166")
                                            self.window.confirmar.show()
                                            self.observacao_r.show()
                                            self.observacao_r.setText(
                                                "Acesso permitido para locais abertos"
                                            )
                                            self.observacao_r.setStyleSheet(
                                                "background-color: rgb(73, 122, 166);\n"
                                                "color: rgb(255, 255, 255);\n"
                                                'font: 75 14pt "Arial";\n'
                                                "padding-top:5px;\n"
                                                "padding-left: 5px;\n"
                                                "align: center;"
                                            )
                                            if quantidade == 2 or quantidade == 3:
                                                self.window.p_dose.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.fig_vac_r.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.p_dose_n_r.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.s_dose.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.fig_vac_r_2.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.s_dose_n_r.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )

                                            elif (
                                                quantidade == 1
                                                and fabricante.lower() == "janssen_j&j"
                                            ):
                                                self.window.p_dose.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.fig_vac_r.setStyleSheet(
                                                    "image: url(:/newPrefix/2646111.png);\n"
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                                self.window.p_dose_n_r.setStyleSheet(
                                                    "background-color: rgb(73, 122, 166);"
                                                )
                                    
                                elif resposta is True:
                                    self.window.regi_saida.show()
                                    self.text_saida.setText(f"Registrando saída\nàs {h_saida}")
                                    self.text_saida.setStyleSheet(
                                        "background-color: rgb(73, 122, 166);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        'font: 75 14pt "Arial";\n'
                                        "padding-top:5px;\n"
                                        "padding-left: 5px;\n"
                                        "align: center;"
                                    )
                                    sleep(3)
                                    self.window.regi_saida.close()
                                elif resposta is not True and resposta is not False:
                                    self.window.regi_saida.show()
                                    self.text_saida.setText(resposta)
                                    self.text_saida.setStyleSheet(
                                        "background-color: rgb(73, 122, 166);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        'font: 75 14pt "Arial";\n'
                                        "padding-top:5px;\n"
                                        "padding-left: 5px;\n"
                                        "align: center;"
                                    )
                                    sleep(3)
                                    self.window.regi_saida.close()

                            elif verificacao is not False and verificacao is not True:
                                # VERIFICA A HORA E O DIA ATUAL DO SISTEMA E COMPARA COM A HORA DE CHEGADA DO ALUNO E O DIA SOLICITADO
                                # CASO O ALUNO ESTEJA FORA DO HORÁRIO OU DO DIA RESERVADO, O ACESSO SERÁ NEGADO

                                self.window.regi_saida.show()
                                self.text_saida.setText(verificacao)
                                self.text_saida.setStyleSheet(
                                    "background-color: rgb(73, 122, 166);\n"
                                    "color: rgb(255, 255, 255);\n"
                                    'font: 75 16pt "Arial";\n'
                                    "padding-top:5px;\n"
                                    "padding-left: 5px;\n"
                                    "align: center;"
                                )
                                sleep(7)
                                self.window.regi_saida.close()

                elif ok is False:
                    self.window.CAPA.show()

                if self.cart_vac == 1:
                    print('tudo certo aqui')
                    ###################################################################
                    bytes = b64decode(carteirinha, validate=True)
                    if bytes[0:4] != b'%PDF':
                        raise ValueError('Missing the PDF file signature')

                    # Write the PDF contents to a local file
                    f = open('vac_carterinha.pdf', 'wb')
                    f.write(bytes)
                    f.close()
                    view = QWebEngineView()
                    view.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
                    view.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
                    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
                    view.load(QtCore.QUrl("%s" % (QtCore.QUrl.fromLocalFile(os.path.join(CURRENT_DIR, "vac_carterinha.pdf")).toString())))
                    view.setGeometry(0, 28, 1000, 750)
                    view.setWindowTitle("Carteira de Vacina")
                    view.setWindowIcon(QIcon("icon.ico"))
                    view.show()
                    self.cart_vac = 0
                    ###################################################################

                if self.logic == 2:
                    print ('terceiro logic', self.logic)
                    continue

                elif self.logic == 3:
                    print ('quarto logic', self.logic)
                    break

                elif self.logic == 4:
                    # FECHA A CAMERA
                    self.cap.release()
                    self.window.imgLabel.close()
                    self.window.fechar_camera.close()
                    self.window.abrir_camera.show()
                    self.logic = 0
                    self.window.CAPA.show()

        except:
            self.window.regi_saida.show()
            self.text_saida.setText("Ocorreu um erro\nPor favor, contatar o técnico")
            self.text_saida.setStyleSheet(
                "background-color: rgb(73, 122, 166);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 75 16pt "Arial";\n'
                "padding-top:5px;\n"
                "padding-left: 5px;\n"
                "align: center;"
            )
            sleep(7)
            self.window.regi_saida.close()
            self.window.imgLabel.close()
            self.window.fechar_camera.close()
            self.window.abrir_camera.show()

        self.cap.release()
        cv2.destroyAllWindows()

    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("Deseja retornar à tela de login?")
        close.setStyleSheet(
            "background-color: rgb(255,255,255);\n"
            "color: rgb(28, 41, 48);\n"
            'font: 75 12pt "Arial";\n'
        )

        close.setWindowTitle("SCAC - Minha Vida Acadêmica")
        close.setWindowIcon(QIcon("icon.ico"))
        close.setIcon(QMessageBox.Warning)
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        close = close.exec()
        if close == QMessageBox.Yes:
            self.logic = 3
            print ('sexto logic', self.logic)
            self.window.close()
            confirma(cond=True)
        elif close == QMessageBox.Cancel:
            if not type(event) == bool:
                event.ignore()
                self.logic = 2

    def CloseCapture(self):
        self.window.habilita_carteinha.close()
        self.logic = 4
        print('CloseCapture', self.logic)
       

    def habilitar_carteirinha(self):
        self.window.habilita_carteinha.show()
        #self.window.desabilita_carteinha.show()

        self.cart_vac = 1

    def desabilitar_carteinha(self):
        #self.window.desabilita_carteinha.close()
        self.window.habilita_carteinha.show()

        self.cart_vac = 0

    def opcao_temp(self):
        self.window.aviso_temp.show()

    def autorizar(self):
        self.window.fechar_confirma.show()
        self.window.fechar_negar.show()
        detalhes(self.window, "73", "122", "166")
        self.window.observacao.close()
        self.opcao_temp()

    def seguinte(self):
        self.window.regi_saida.show()
        self.window.proximo.close() 
        self.text_saida.setText('Passe novamente o seu\n QR-code para confirmarmos\n sua entrada!')
        self.regi_saida.setStyleSheet(
            'padding: 25px;\n'
            'border-radius: 3px\n;'
            "background-color: #299969;\n"
            "border-color: #f4a911;\n"
            "color: #FFF;\n"
            'font: 75 16pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;\n"
            "align: center;"
        )
        self.text_saida.setStyleSheet(
            'padding: 25px;\n'
            'border-radius: 3px\n;'
            "background-color: #299969;\n"
            "border-color: #f4a911;\n"
            "color: #FFF;\n"
            "padding-top:5px;\n"
            "padding-left: 5px;\n"
            "align: center;"	
        )
        sleep(7)
        self.window.regi_saida.close()

    def nao_autorizar(self):
        self.window.fechar_confirma.show()
        self.window.fechar_negar.show()
        detalhes(self.window, "255", "0", "0")
        self.observacao.setStyleSheet(
            "background-color: rgb(255, 0, 0);\n"
            "color: rgb(0, 0, 0);\n"
            'font: 75 12pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;"
        )
        self.window.observacao.show()
        self.observacao.setText("Não cumpriu os requisitos mínimos")
        sleep(5)
        normal(self.window)
        self.window.fechar_confirma.close()
        self.window.fechar_negar.close()
        self.window.CAPA.show()

    def opcao_nao(self):
        normal(self.window)
        hora_ini = HORARIO_ATUAL
        temp = None
        dict_dados = {"entrada": hora_ini, "saida": "00:00:00", "temperatura": temp}
        response = enviar_dados(util.token, util.matricula, dict_dados, util.id_discente)
        self.window.regi_saida.show()
        self.text_saida.setText(response)
        self.text_saida.setStyleSheet(
            "background-color: rgb(73, 122, 166);\n"
            "color: rgb(255, 255, 255);\n"
            'font: 75 16pt "Arial";\n'
            "padding-top:5px;\n"
            "padding-left: 5px;\n"
            "align: center;"
        )
        sleep(7)
        self.window.regi_saida.close()
        self.window.fechar_confirma.close()
        self.window.fechar_negar.close()
        self.window.CAPA.show()

    def permitir(self):
        try:
            self.opcao_nao()
            self.window.regi_saida.show()
            self.text_saida.setText("Entrada foi registrada\nna base de dados")
            self.text_saida.setStyleSheet(
                "background-color: rgb(73, 122, 166);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 75 16pt "Arial";\n'
                "padding-top:5px;\n"
                "padding-left: 5px;\n"
                "align: center;"
            )
            sleep(3)
            normal(self.window)
            self.window.regi_saida.close()
            self.window.CAPA.show()
        except:
            self.window.regi_saida.show()
            self.text_saida.setText(
                f"Problema ao registrar a entrada\nContatar o servidor técnico"
            )
            self.text_saida.setStyleSheet(
                "background-color: rgb(73, 122, 166);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 75 16pt "Arial";\n'
                "padding-top:5px;\n"
                "padding-left: 5px;\n"
                "align: center;"
            )
            sleep(3)
            normal(self.window)
            self.window.regi_saida.close()
            self.window.CAPA.show()

    def opcao_sim(self):
        self.window.temp.show()
        self.window.aviso_temp.close()

    def salvar_temp(self):
        temperatura = self.window.temperatura.text()
        hora_ini = HORARIO_ATUAL
        try:
            dict_dados = {
                "entrada": hora_ini,
                "saida": "00:00:00",
                "temperatura": float(temperatura),
            }
            response = enviar_dados(util.token, util.matricula, dict_dados, util.id_discente)
            self.window.regi_saida.show()
            self.text_saida.setText(response)
            self.text_saida.setStyleSheet(
                "background-color: rgb(73, 122, 166);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 75 16pt "Arial";\n'
                "padding-top:5px;\n"
                "padding-left: 5px;\n"
                "align: center;"
            )
            sleep(4)
            self.window.regi_saida.close()
            self.window.aviso_2.setText("Insira a temperatura")
            self.window.aviso_1.setText("Apenas Números")
            self.window.temp.close()
            temperatura = self.window.temperatura.clear()
            normal(self.window)
            self.window.fechar_confirma.close()
            self.window.fechar_negar.close()
            self.window.CAPA.show()

        except:
            self.window.aviso_2.setText(response)
            self.window.aviso_1.setText("")
            sleep(3)
            self.window.aviso_2.setText("Insira a temperatura")
            self.window.aviso_1.setText("Apenas Números")
            self.window.temp.close()
            temperatura = self.window.temperatura.clear()

    