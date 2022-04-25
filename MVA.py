from PyQt5 import QtWidgets
from util import Token, sleep
from conexao import login
from PyQt5.QtCore import QEventLoop, QTimer
import sys_qr_code
from PyQt5.uic import loadUi
import sys

app = QtWidgets.QApplication(sys.argv)
tela_login = loadUi("login.ui")

# FUNÇÃO QUE CHAMA A CLASSE DE LEITURA DE QR_CODE


def main():
    window = sys_qr_code.sis_qr_code()
    window.showMaximized()


# FUNÇÃO DA TELA DE LOGIN
def tela_cam():
    tela_login.aviso.setText("")
    tela_login.senha.setEchoMode(QtWidgets.QLineEdit.Password)
    usuario = tela_login.usuario.text()
    sys_qr_code.USER = usuario
    senha = tela_login.senha.text()
    token, res, tipo = login(usuario, senha)
    if res:
        Token(token)
        # tipo = verifica_tipo(token)
        # Tipo(tipo)
        verif_tipo = tipo
        print(verif_tipo)
        if verif_tipo == 0 or verif_tipo == 1 or verif_tipo == 4:
            tela_login.hide()
            tela_login.usuario.clear()
            tela_login.senha.clear()
            print('xnbshvb')
            main()
        else:
            tela_login.aviso.show()
            tela_login.aviso.setText("Perfil não permitido!!")
            tela_login.aviso.setStyleSheet(
                            'padding: 25px;\n'
                            'border: 1px solid gray;\n'
                            'border-radius: 3px\n;'
                            'margin: 35px;\n'
                            'font-size: 16px;\n'
                            'border-color: #e8273b;\n'
                            'color: rgb(255, 0, 0);\n'
                            'background-color: #ffdddd;\n'
            )
            sleep(7)
            tela_login.aviso.close()
    elif res is False:
        tela_login.aviso.show()
        tela_login.aviso.setText("Usuário ou senha incorretos")
        tela_login.aviso.setStyleSheet(
                            'padding: 25px;\n'
                            'border: 1px solid gray;\n'
                            'border-radius: 3px\n;'
                            'margin: 35px;\n'
                            'font-size: 14px;\n'
                            'border-color: #e8273b;\n'
                            'color: rgb(255, 0, 0);\n'
                            'background-color: #ffdddd;\n'
            )
        sleep(7)
        tela_login.aviso.close()
        """loop = QEventLoop()
        QTimer.singleShot(3000, loop.quit)
        loop.exec_()
        tela_login.aviso.setText("")"""
    elif res is not True and res is not False:
        tela_login.aviso.setText(res)
        loop = QEventLoop()
        QTimer.singleShot(3000, loop.quit)
        loop.exec_()
        tela_login.aviso.setText("")


def confirma(cond):
    if cond is True:
        tela_login.enviar.clicked.connect(tela_cam)
        # tela_login.show()
        tela_login.showMaximized()
    else:
        pass


if __name__ == "__main__":
    tela_login.enviar.clicked.connect(tela_cam)
    tela_login.show()
    tela_login.showMaximized()
    try:
        sys.exit(app.exec_())
    except:
        print("Acabou! Acabou o programa!")
