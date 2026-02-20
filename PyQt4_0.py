import sys
import requests
import google.generativeai as genai
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QPushButton, QTextEdit, QDateEdit, QFileDialog, 
                             QHBoxLayout, QStackedWidget)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QDate, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from deep_translator import GoogleTranslator
from PIL import Image
import io
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def traduzir_texto(texto):
    try:
        if not texto or texto == "No explanation":
            return "Sem descrição disponível."
        return GoogleTranslator(source='auto', target='pt').translate(texto)
    except:
        return "Erro na tradução automática."

def gerar_relatorio_ia(url_imagem):
    try:
        response_img = requests.get(url_imagem, timeout=10)
        img = Image.open(io.BytesIO(response_img.content))

        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = "Analise esta imagem astronômica da NASA e faça um relatório científico resumido em português brasileiro."
        
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"A IA não conseguiu analisar a imagem agora. (Erro: {str(e)})"

def carregar_conteudo():
    data_str = calendario.date().toString("yyyy-MM-dd")
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={data_str}"

    titulo_label.setText("Buscando dados na NASA...")
    descricao_box.setPlainText("Aguarde, processando...")
    QApplication.processEvents()

    try:
        res = requests.get(url).json()
    
        titulo_en = res.get('title', 'No Title')
        expl_en = res.get('explanation', 'No explanation')
        titulo_pt = traduzir_texto(titulo_en)
        expl_pt = traduzir_texto(expl_en)
        
        media_url = res.get('url', '')
        media_type = res.get('media_type', '')

        titulo_label.setText(f"🇧🇷 {titulo_pt}\n🇺🇸 ({titulo_en})")

        texto_final = "--- DESCRIÇÃO (PORTUGUÊS) ---\n"
        texto_final += f"{expl_pt}\n\n"
        texto_final += "--- DESCRIPTION (ENGLISH) ---\n"
        texto_final += f"{expl_en}\n\n"

        if media_type == 'image':
            stack.setCurrentIndex(0)
            img_data = requests.get(media_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            imagem_label.setPixmap(pixmap.scaled(700, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            relatorio = gerar_relatorio_ia(media_url)
            texto_final += "=================\n"
            texto_final += "ANÁLISE GEMINI IA\n"
            texto_final += "=================\n"
            texto_final += f"{relatorio}"
        
        elif media_type == 'video':
            stack.setCurrentIndex(1)
            video_view.setUrl(QUrl(media_url))
            texto_final += "\n[Vídeo detectado. Análise de IA disponível apenas para fotos.]"

        descricao_box.setPlainText(texto_final)
    except Exception as e:
        descricao_box.setPlainText(f"Erro ao carregar: {str(e)}")

def mudar_data(dias):
    nova_data = calendario.date().addDays(dias)
    if nova_data <= QDate.currentDate():
        calendario.setDate(nova_data)
        carregar_conteudo()

def salvar_imagem():
    if stack.currentIndex() == 0 and imagem_label.pixmap():
        path, _ = QFileDialog.getSaveFileName(None, "Salvar Imagem", "", "Images (*.jpg *.png)")
        if path:
            imagem_label.pixmap().save(path)

app = QApplication(sys.argv)

janela = QWidget()
janela.setWindowTitle("Ver imagens daoras da NASA")
janela.resize(900, 950)
layout_principal = QVBoxLayout()

layout_nav = QHBoxLayout()
btn_anterior = QPushButton("◀ Anterior")
btn_proximo = QPushButton("Próximo ▶")
calendario = QDateEdit()
calendario.setCalendarPopup(True)
calendario.setDate(QDate.currentDate())
calendario.setMaximumDate(QDate.currentDate())

layout_nav.addWidget(btn_anterior)
layout_nav.addWidget(calendario)
layout_nav.addWidget(btn_proximo)

btn_carregar = QPushButton("Explorar o Universo")
btn_carregar.setStyleSheet("background-color: #0B3D91; color: white; font-weight: bold; height: 40px;")

titulo_label = QLabel("Escolha uma data e clique em Explorar")
titulo_label.setAlignment(Qt.AlignCenter)
titulo_label.setWordWrap(True)
titulo_label.setFont(QFont("Arial", 11, QFont.Bold))

stack = QStackedWidget()
imagem_label = QLabel("A imagem aparecerá aqui")
imagem_label.setAlignment(Qt.AlignCenter)
imagem_label.setMinimumHeight(450)
imagem_label.setStyleSheet("border: 1px solid #333; background-color: #f0f0f0;")

video_view = QWebEngineView()
video_view.setMinimumHeight(450)

stack.addWidget(imagem_label)
stack.addWidget(video_view)

descricao_box = QTextEdit()
descricao_box.setReadOnly(True)
descricao_box.setFont(QFont("Segoe UI", 10))

btn_salvar = QPushButton("Salvar Imagem Atual")

layout_principal.addLayout(layout_nav)
layout_principal.addWidget(btn_carregar)
layout_principal.addWidget(titulo_label)
layout_principal.addWidget(stack)
layout_principal.addWidget(descricao_box)
layout_principal.addWidget(btn_salvar)

janela.setLayout(layout_principal)

btn_carregar.clicked.connect(carregar_conteudo)
btn_anterior.clicked.connect(lambda: mudar_data(-1))
btn_proximo.clicked.connect(lambda: mudar_data(1))
btn_salvar.clicked.connect(salvar_imagem)

janela.show()
sys.exit(app.exec_())