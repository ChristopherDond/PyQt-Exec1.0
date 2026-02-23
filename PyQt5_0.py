import sys
import requests
import os
from dotenv import load_dotenv
from groq import Groq
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QPushButton, QTextEdit, QDateEdit, QFileDialog, 
                             QHBoxLayout, QStackedWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QDate, QUrl
from deep_translator import GoogleTranslator

load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def traduzir_texto(texto):
    try:
        if not texto or texto == "No explanation":
            return "Sem descrição disponível."
        return GoogleTranslator(source='auto', target='pt').translate(texto)
    except:
        return "Erro na tradução automática."

def gerar_relatorio_ia(descricao_nasa):
    try:
        prompt = (
            f"Com base na descrição astronômica fornecida, escreva um relatório detalhado em português brasileiro. "
            f"O relatório deve contar a história por trás desta foto, explicando o que ela representa, os fenômenos envolvidos e sua importância científica. "
            f"REGRAS DE FORMATAÇÃO: Não use asteriscos (*), hashtags (#) ou símbolos de marcação Markdown, deixe apenas o texto puro. "
            f"Para destacar títulos ou termos importantes, escreva-os em LETRAS MAIÚSCULAS. "
            f"Use parágrafos claros e fluidos. Descrição: {descricao_nasa}"
        )
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"ERRO NO PROCESSAMENTO DA IA: {str(e)}"

def carregar_conteudo():
    data_str = calendario.date().toString("yyyy-MM-dd")
    api_key = NASA_API_KEY if NASA_API_KEY else "DEMO_KEY"
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&date={data_str}"

    titulo_label.setText("CONECTANDO COM A NASA...")
    descricao_box.setPlainText("PROCESSANDO DADOS E GERANDO RELATÓRIO...")
    QApplication.processEvents()

    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            descricao_box.setPlainText(f"ERRO NASA: {response.status_code}\n{response.text}")
            return

        res = response.json()
        titulo_en = res.get('title', 'No Title')
        expl_en = res.get('explanation', 'No explanation')
        titulo_pt = traduzir_texto(titulo_en)
        expl_pt = traduzir_texto(expl_en)
        media_url = res.get('url', '')
        media_type = res.get('media_type', '')

        titulo_label.setText(f"{titulo_pt.upper()}\n({titulo_en.upper()})")

        if media_type == 'image':
            stack.setCurrentIndex(0)
            img_data = requests.get(media_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            imagem_label.setPixmap(pixmap.scaled(700, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            relatorio_ia = gerar_relatorio_ia(expl_en)
            
            texto_final = "TEXTO ORIGINAL (INGLÊS)\n"
            texto_final += "="*40 + "\n"
            texto_final += f"{expl_en}\n\n"
            
            texto_final += "TRADUÇÃO (PORTUGUÊS)\n"
            texto_final += "="*40 + "\n"
            texto_final += f"{expl_pt}\n\n"
            
            texto_final += "HISTÓRIA E ANÁLISE DA IA\n"
            texto_final += "="*40 + "\n"
            texto_final += f"{relatorio_ia}"
        
        elif media_type == 'video':
            stack.setCurrentIndex(1)
            video_view.setUrl(QUrl(media_url))
            texto_final = "CONTEÚDO EM VÍDEO DETECTADO.\n\n"
            texto_final += "ORIGINAL:\n" + expl_en + "\n\n"
            texto_final += "TRADUÇÃO:\n" + expl_pt

        descricao_box.setPlainText(texto_final)
        descricao_box.verticalScrollBar().setValue(0)
        
    except Exception as e:
        descricao_box.setPlainText(f"ERRO CRÍTICO: {str(e)}")

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
janela.setWindowTitle("NASA EXPLORER - RELATÓRIOS CIENTÍFICOS")
janela.resize(900, 950)
layout_principal = QVBoxLayout()

layout_nav = QHBoxLayout()
btn_anterior = QPushButton("ANTERIOR")
btn_proximo = QPushButton("PRÓXIMO")
calendario = QDateEdit()
calendario.setCalendarPopup(True)
calendario.setDate(QDate.currentDate())
calendario.setMaximumDate(QDate.currentDate())
layout_nav.addWidget(btn_anterior)
layout_nav.addWidget(calendario)
layout_nav.addWidget(btn_proximo)

btn_carregar = QPushButton("EXPLORAR UNIVERSO")
btn_carregar.setStyleSheet("background-color: #0B3D91; color: white; font-weight: bold; height: 45px; border-radius: 5px;")

titulo_label = QLabel("SELECIONE UMA DATA")
titulo_label.setAlignment(Qt.AlignCenter)
titulo_label.setWordWrap(True)
titulo_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

stack = QStackedWidget()
imagem_label = QLabel()
imagem_label.setAlignment(Qt.AlignCenter)
imagem_label.setMinimumHeight(450)
imagem_label.setStyleSheet("background-color: #000; border: 2px solid #333;")
video_view = QWebEngineView()
video_view.setMinimumHeight(450)
stack.addWidget(imagem_label)
stack.addWidget(video_view)

descricao_box = QTextEdit()
descricao_box.setReadOnly(True)
descricao_box.setFont(QFont("Consolas", 10))
descricao_box.setStyleSheet("background-color: #f9f9f9; padding: 10px;")

btn_salvar = QPushButton("SALVAR IMAGEM")

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