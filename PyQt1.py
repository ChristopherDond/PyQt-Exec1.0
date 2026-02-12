import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QDateEdit, QComboBox
)
from PyQt5.QtCore import QDate

def validar():
    erros = []
    campos = {
        "Nome Completo": nome.text(),
        "CPF": cpf.text(),
        "Nome da mae": nome_mae.text(),
        "RG": rg.text(),
        "Rua/Logradouro": logradouro.text(),
        "Numero": numero.text(),
        "Bairro": bairro.text(),
        "Cidade": cidade.text()
    }

    for nome_campo, valor in campos.items():
        if not valor.strip() or "_" in valor:
            erros.append(nome_campo)

    if erros:
        lista_erros = "\n- ".join(erros)
        QMessageBox.warning(
            janela, 
            "Campos nao preenchidos", 
            f"Ainda existem campos vazios:\n\n- {lista_erros}"
        )
    else:
        QMessageBox.information(janela, 'Sucesso', 'Dados cadastrados!')
        limpar()

def limpar():
    for widget in janela.findChildren(QLineEdit):
        widget.clear()
    data_nasc.setDate(QDate.currentDate())
    uf.setCurrentIndex(0)
    nome.setFocus()

app = QApplication(sys.argv)

janela = QWidget()
janela.setWindowTitle('Cadastro')
janela.setFixedSize(700, 600)

#pessoa
QLabel("Nome Completo:", janela).setGeometry(20, 10, 200, 20)
nome = QLineEdit(janela)
nome.setGeometry(20, 35, 660, 25)

QLabel("CPF:", janela).setGeometry(20, 70, 100, 20)
cpf = QLineEdit(janela)
cpf.setInputMask("000.000.000-00;_")
cpf.setGeometry(20, 95, 320, 25)

QLabel("Data de Nascimento:", janela).setGeometry(360, 70, 200, 20)
data_nasc = QDateEdit(janela)
data_nasc.setCalendarPopup(True)
data_nasc.setDate(QDate(2000, 1, 1))
data_nasc.setGeometry(360, 95, 320, 25)

QLabel("RG:", janela).setGeometry(20, 190, 100, 20)
rg = QLineEdit(janela)
rg.setInputMask("00.000.000-0;_")
rg.setGeometry(20, 215, 320, 25)

#mae
QLabel("Nome da mae:", janela).setGeometry(20, 130, 200, 20)
nome_mae = QLineEdit(janela)
nome_mae.setGeometry(20, 155, 660, 25)

#td q tem ave com endereço
QLabel("Rua/Logradouro:", janela).setGeometry(20, 250, 200, 20)
logradouro = QLineEdit(janela)
logradouro.setGeometry(20, 275, 660, 25)

QLabel("Número:", janela).setGeometry(20, 310, 100, 20)
numero = QLineEdit(janela)
numero.setGeometry(20, 335, 320, 25)

QLabel("Complemento:", janela).setGeometry(360, 310, 100, 20)
complemento = QLineEdit(janela)
complemento.setGeometry(360, 335, 320, 25)

QLabel("Bairro:", janela).setGeometry(20, 370, 100, 20)
bairro = QLineEdit(janela)
bairro.setGeometry(20, 395, 320, 25)

QLabel("Cidade:", janela).setGeometry(360, 370, 100, 20)
cidade = QLineEdit(janela)
cidade.setGeometry(360, 395, 320, 25)

QLabel("UF:", janela).setGeometry(20, 430, 50, 20)
uf = QComboBox(janela)
uf_lista = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]
uf.addItems(uf_lista)
uf.setGeometry(20, 455, 100, 25)

#os butao
butao_cadastrar = QPushButton("Cadastrar", janela)
butao_cadastrar.setGeometry(20, 520, 320, 50)
butao_cadastrar.clicked.connect(validar)

butao_limpar = QPushButton("Limpar", janela)
butao_limpar.setGeometry(360, 520, 320, 50)
butao_limpar.clicked.connect(limpar)

janela.show()
sys.exit(app.exec_())