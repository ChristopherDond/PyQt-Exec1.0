import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit
from PyQt5.QtGui import QFont

app = QApplication(sys.argv)

janela = QWidget()
janela.setWindowTitle('Cripto Direto')
janela.resize(450, 450) # Aumentei um pouco a altura para caber os dois preços

app.setStyleSheet("""
    QLabel { font-size: 20px; }
    QLineEdit { font-size: 20px; border: 1px solid gray; }
    QPushButton { font-size: 20px; }
""")

titulo = QLabel("Buscador de Moeda", janela)
titulo.setFont(QFont('Arial', 24, QFont.Bold))
titulo.setGeometry(20, 30, 410, 40)

campo_moeda = QLineEdit(janela)
campo_moeda.setPlaceholderText("Digite o nome (ex: bitcoin)")
campo_moeda.setGeometry(20, 100, 410, 50)

botao_buscar = QPushButton("Consultar", janela)
botao_buscar.setGeometry(20, 170, 410, 60)

# Ajustado para suportar duas linhas de texto
resultado_label = QLabel("Preço: ---", janela)
resultado_label.setGeometry(20, 250, 410, 120) 
resultado_label.setStyleSheet("font-size: 24px;")
resultado_label.setWordWrap(True) 

def buscar():
    moeda = campo_moeda.text().lower().strip()

    if not moeda:
        resultado_label.setText("Erro: Digite algo!")
        resultado_label.setStyleSheet("color: orange; font-size: 24px;")
        campo_moeda.clear()
        return

    resultado_label.setText("Buscando...")
    resultado_label.setStyleSheet("color: black; font-size: 24px;")
    app.processEvents()

    try:
        # Alterado: Adicionado 'usd' na consulta vs_currencies
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={moeda}&vs_currencies=brl,usd"
        req = requests.get(url, timeout=5)
        req.raise_for_status()
        dados = req.json()

        if moeda in dados:
            preco_brl = dados[moeda]['brl']
            preco_usd = dados[moeda]['usd']
            
            # Formatação com as duas moedas
            texto_resultado = f"R$ {preco_brl:,.2f}\nUS$ {preco_usd:,.2f}"
            
            resultado_label.setText(texto_resultado)
            resultado_label.setStyleSheet("color: blue; font-size: 28px; font-weight: bold;")
        else:
            resultado_label.setText("Moeda não encontrada.")
            resultado_label.setStyleSheet("color: red; font-size: 22px;")
            campo_moeda.clear()

    except Exception:
        resultado_label.setText("Erro: Sem conexão.")
        resultado_label.setStyleSheet("color: red; font-size: 22px;")
        campo_moeda.clear()

botao_buscar.clicked.connect(buscar)

janela.show()
sys.exit(app.exec_())