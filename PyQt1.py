import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QDateEdit, QComboBox
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont

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
            "Campos não preenchidos", 
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
janela.setWindowTitle('Sistema de Cadastro')
janela.setFixedSize(700, 680)  # Aumentei a altura para caber os botões
janela.setStyleSheet("""
    QWidget {
        background-color: #f5f6fa;
        font-family: Arial;
    }
    QLabel {
        color: #2c3e50;
        font-weight: bold;
        font-size: 11px;
        text-transform: uppercase;
    }
    QLineEdit, QDateEdit, QComboBox {
        background-color: white;
        border: 2px solid #dcdde1;
        border-radius: 5px;
        padding: 5px;
        font-size: 13px;
    }
    QLineEdit:focus, QDateEdit:focus, QComboBox:focus {
        border: 2px solid #3498db;
    }
""")

# pessoa/personal informations
QLabel("Nome Completo:", janela).setGeometry(20, 10, 200, 20)
nome = QLineEdit(janela)
nome.setGeometry(20, 35, 660, 35)
nome.setPlaceholderText("Digite seu nome completo")

QLabel("CPF:", janela).setGeometry(20, 80, 100, 20)
cpf = QLineEdit(janela)
cpf.setInputMask("000.000.000-00;_")
cpf.setGeometry(20, 105, 320, 35)
cpf.setPlaceholderText("000.000.000-00")

QLabel("Data de Nascimento:", janela).setGeometry(360, 80, 200, 20)
data_nasc = QDateEdit(janela)
data_nasc.setCalendarPopup(True)
data_nasc.setDate(QDate(2000, 1, 1))
data_nasc.setGeometry(360, 105, 320, 35)

QLabel("RG:", janela).setGeometry(20, 150, 100, 20)
rg = QLineEdit(janela)
rg.setInputMask("00.000.000-0;_")
rg.setGeometry(20, 175, 320, 35)
rg.setPlaceholderText("00.000.000-0")

# nome da mae/mom name
QLabel("Nome da mãe:", janela).setGeometry(20, 220, 200, 20)
nome_mae = QLineEdit(janela)
nome_mae.setGeometry(20, 245, 660, 35)
nome_mae.setPlaceholderText("Digite o nome completo da mãe")

# endereço/address
QLabel("Rua/Logradouro:", janela).setGeometry(20, 290, 200, 20)
logradouro = QLineEdit(janela)
logradouro.setGeometry(20, 315, 660, 35)
logradouro.setPlaceholderText("Digite o nome da rua")

QLabel("Número:", janela).setGeometry(20, 360, 100, 20)
numero = QLineEdit(janela)
numero.setGeometry(20, 385, 320, 35)
numero.setPlaceholderText("Nº")

QLabel("Complemento:", janela).setGeometry(360, 360, 100, 20)
complemento = QLineEdit(janela)
complemento.setGeometry(360, 385, 320, 35)
complemento.setPlaceholderText("Apto, Bloco, etc")

QLabel("Bairro:", janela).setGeometry(20, 430, 100, 20)
bairro = QLineEdit(janela)
bairro.setGeometry(20, 455, 320, 35)
bairro.setPlaceholderText("Digite o bairro")

QLabel("Cidade:", janela).setGeometry(360, 430, 100, 20)
cidade = QLineEdit(janela)
cidade.setGeometry(360, 455, 320, 35)
cidade.setPlaceholderText("Digite a cidade")

QLabel("UF:", janela).setGeometry(20, 500, 50, 20)
uf = QComboBox(janela)
uf_lista = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]
uf.addItems(uf_lista)
uf.setGeometry(20, 525, 100, 35)

# botoes com estilo agora
# buttons with new styles
butao_cadastrar = QPushButton("CADASTRAR", janela)
butao_cadastrar.setGeometry(20, 590, 320, 45)
butao_cadastrar.setStyleSheet("""
    QPushButton {
        background-color: #27ae60;
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
    }
    QPushButton:hover {
        background-color: #2ecc71;
    }
    QPushButton:pressed {
        background-color: #229954;
    }
""")
butao_cadastrar.clicked.connect(validar)

butao_limpar = QPushButton("LIMPAR", janela)
butao_limpar.setGeometry(360, 590, 320, 45)
butao_limpar.setStyleSheet("""
    QPushButton {
        background-color: #e67e22;
        color: white;
        border: none;
        border-radius: 5px;
        font-weight: bold;
        font-size: 14px;
        text-transform: uppercase;
    }
    QPushButton:hover {
        background-color: #f39c12;
    }
    QPushButton:pressed {
        background-color: #d35400;
    }
""")
butao_limpar.clicked.connect(limpar)

janela.show()
sys.exit(app.exec_())