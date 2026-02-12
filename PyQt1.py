import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QDateEdit, QComboBox
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont

def consultar_cep():
    # Remove caracteres não numéricos da máscara
    cep_digits = cep.text().replace("-", "").replace("_", "").strip()
    
    if len(cep_digits) != 8:
        return # Não busca se o CEP estiver incompleto

    url = f"https://viacep.com.br/ws/{cep_digits}/json/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            if "erro" in dados:
                QMessageBox.warning(janela, "Erro", "CEP não encontrado.")
            else:
                logradouro.setText(dados.get("logradouro", ""))
                bairro.setText(dados.get("bairro", ""))
                cidade.setText(dados.get("localidade", ""))
                
                # Ajusta o ComboBox da UF
                sigla_uf = dados.get("uf", "")
                index = uf.findText(sigla_uf)
                if index >= 0:
                    uf.setCurrentIndex(index)
                
                numero.setFocus()
        else:
            QMessageBox.critical(janela, "Erro", "Falha na conexão com o serviço de CEP.")
    except Exception as e:
        QMessageBox.critical(janela, "Erro", f"Ocorreu um erro: {str(e)}")

def validar():
    erros = []
    campos = {
        "Nome Completo": nome.text(),
        "CPF": cpf.text(),
        "CEP": cep.text(),
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
    data_nasc.setDate(QDate(2000, 1, 1))
    uf.setCurrentIndex(0)
    nome.setFocus()

app = QApplication(sys.argv)

janela = QWidget()
janela.setWindowTitle('Sistema de Cadastro com ViaCEP')
janela.setFixedSize(700, 720) 
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

# --- INFORMAÇÕES PESSOAIS ---
QLabel("Nome Completo:", janela).setGeometry(20, 10, 200, 20)
nome = QLineEdit(janela)
nome.setGeometry(20, 35, 660, 35)
nome.setPlaceholderText("Digite seu nome completo")

QLabel("CPF:", janela).setGeometry(20, 80, 100, 20)
cpf = QLineEdit(janela)
cpf.setInputMask("000.000.000-00;_")
cpf.setGeometry(20, 105, 320, 35)

QLabel("Data de Nascimento:", janela).setGeometry(360, 80, 200, 20)
data_nasc = QDateEdit(janela)
data_nasc.setCalendarPopup(True)
data_nasc.setDate(QDate(2000, 1, 1))
data_nasc.setGeometry(360, 105, 320, 35)

QLabel("RG:", janela).setGeometry(20, 150, 100, 20)
rg = QLineEdit(janela)
rg.setInputMask("00.000.000-0;_")
rg.setGeometry(20, 175, 320, 35)

QLabel("Nome da mãe:", janela).setGeometry(20, 220, 200, 20)
nome_mae = QLineEdit(janela)
nome_mae.setGeometry(20, 245, 660, 35)

# --- ENDEREÇO COM VIACEP ---
QLabel("CEP (Busca automática):", janela).setGeometry(20, 290, 200, 20)
cep = QLineEdit(janela)
cep.setInputMask("00000-000;_")
cep.setGeometry(20, 315, 200, 35)
# Conecta a função de busca quando o usuário termina de digitar o CEP
cep.editingFinished.connect(consultar_cep) 

QLabel("Rua/Logradouro:", janela).setGeometry(20, 360, 200, 20)
logradouro = QLineEdit(janela)
logradouro.setGeometry(20, 385, 660, 35)

QLabel("Número:", janela).setGeometry(20, 430, 100, 20)
numero = QLineEdit(janela)
numero.setGeometry(20, 455, 150, 35)

QLabel("Complemento:", janela).setGeometry(190, 430, 100, 20)
complemento = QLineEdit(janela)
complemento.setGeometry(190, 455, 490, 35)

QLabel("Bairro:", janela).setGeometry(20, 500, 100, 20)
bairro = QLineEdit(janela)
bairro.setGeometry(20, 525, 320, 35)

QLabel("Cidade:", janela).setGeometry(360, 500, 100, 20)
cidade = QLineEdit(janela)
cidade.setGeometry(360, 525, 210, 35)

QLabel("UF:", janela).setGeometry(590, 500, 50, 20)
uf = QComboBox(janela)
uf.addItems([
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", 
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
])
uf.setGeometry(590, 525, 90, 35)

# --- BOTÕES ---
butao_cadastrar = QPushButton("CADASTRAR", janela)
butao_cadastrar.setGeometry(20, 630, 320, 45)
butao_cadastrar.setStyleSheet("""
    QPushButton {
        background-color: #27ae60; color: white; border-radius: 5px; font-weight: bold;
    }
    QPushButton:hover { background-color: #2ecc71; }
""")
butao_cadastrar.clicked.connect(validar)

butao_limpar = QPushButton("LIMPAR", janela)
butao_limpar.setGeometry(360, 630, 320, 45)
butao_limpar.setStyleSheet("""
    QPushButton {
        background-color: #e67e22; color: white; border-radius: 5px; font-weight: bold;
    }
    QPushButton:hover { background-color: #f39c12; }
""")
butao_limpar.clicked.connect(limpar)

janela.show()
sys.exit(app.exec_())