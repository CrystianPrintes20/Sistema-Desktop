from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEngineView
 
def MainWindow(window):
 
    window.setWindowTitle("PDF Viewer")
    window.setGeometry(0, 28, 1000, 750)
    window.centralWidget = QWidget(window)

    window.webView = QWebEngineView()
    window.webView.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
    window.webView.settings().setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
    window.setCentralWidget(window.webView)
 
    def url_changed(window):
        window.setWindowTitle(window.webView.title())
 
    def go_back(window):
        window.webView.back()

def detalhes(window, r, g, b):
    window.nome_aluno.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )
    window.nome_aluno_r.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )

    window.curso.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )
    window.curso_r.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )

    window.hora_ini.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )
    window.hora_ini_r.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )

    window.matricula.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )
    window.matricula_r.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )

    window.hora_fim.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )
    window.data.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )
    window.data_r.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )

    window.espaco_reservado.setStyleSheet(
        "background-color: rgb(%s, %s, %s);\n"
        "color: rgb(255, 255, 255);\n"
        'font: 75 12pt "Arial";\n'
        "padding-top:5px;\n"
        "padding-left: 5px;" % (r, g, b)
    )


def normal(window):
    _translate = QtCore.QCoreApplication.translate
    window.aviso_temp.close()
    window.nome_aluno.setText(_translate("MainWindow", "Nome do Aluno"))
    window.matricula.setText(_translate("MainWindow", "Matricula"))
    window.curso.setText(_translate("MainWindow", "Curso"))
    window.espaco_reservado.setText(_translate("MainWindow", "Espaço Reservado"))
    window.data.setText(_translate("MainWindow", "Data Reservada"))
    window.hora_ini.setText(_translate("MainWindow", "Entrada"))
    window.hora_fim.setText(_translate("MainWindow", "Saída"))
    window.observacao.close()
    detalhes(window, "255", "255", "255")


def displayImage(quadro, img, window=1):
    qformat = QImage.Format_Indexed8
    if len(img.shape) == 3:
        if (img.shape[2]) == 4:
            qformat = QImage.Format_RGBA888
        else:
            qformat = QImage.Format_RGB888
    img = QImage(img, img.shape[1], img.shape[0], qformat)
    img = img.scaled(1250, 700, QtCore.Qt.KeepAspectRatio)
    img = img.rgbSwapped()

    quadro.imgLabel.setPixmap(QPixmap.fromImage(img))
    quadro.imgLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
