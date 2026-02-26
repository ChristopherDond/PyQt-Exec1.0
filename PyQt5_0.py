import sys
import requests
import os
import threading
import asyncio
import edge_tts
import shutil
from dotenv import load_dotenv
from groq import Groq
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QPushButton, QTextEdit, QDateEdit,
                             QHBoxLayout, QStackedWidget, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDate, QUrl
from deep_translator import GoogleTranslator
import pygame
import fal_client
 
load_dotenv()
 
NASA_API_KEY = os.getenv("NASA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAL_KEY = os.getenv("FAL_KEY")
 
client = Groq(api_key=GROQ_API_KEY)
pygame.mixer.init()
 
CAMINHO_IMAGEM_TEMP = "temp_nasa_image.jpg"
NOME_VIDEO_OUTPUT = "nasa_ia_video.mp4"
 
janela_player_global = None
 
class JanelaVideo(QWidget):
    def __init__(self, caminho_video):
        super().__init__()
        self.setWindowTitle("IA VIDEO PLAYER - NASA EXPLORER 2026")
        self.resize(1000, 650)
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout()
       
        self.browser = QWebEngineView()
       
        caminho_url = QUrl.fromLocalFile(caminho_video).toString()
       
        html_content = f"""
            <html>
                <body style="margin:0; background-color:black; display:flex; align-items:center; justify-content:center;">
                    <video width="100%" height="auto" controls autoplay loop>
                        <source src="{caminho_url}" type="video/mp4">
                        Seu navegador não suporta o player de vídeo.
                    </video>
                </body>
            </html>
        """
        self.browser.setHtml(html_content, QUrl.fromLocalFile(os.path.dirname(caminho_video) + "/"))
       
        layout.addWidget(self.browser)
        self.setLayout(layout)
 
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
            f"REGRAS DE FORMATAÇÃO: Não use símbolos Markdown. Use LETRAS MAIÚSCULAS para títulos. "
            f"Descrição: {descricao_nasa}"
        )
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"ERRO IA: {str(e)}"
 
def gerar_video_ia_real():
    if not os.path.exists(CAMINHO_IMAGEM_TEMP):
        QMessageBox.warning(janela, "Erro", "Carregue uma imagem da NASA primeiro!")
        return
 
    def thread_video():
        global janela_player_global
        try:
            print("Iniciando processo no Fal.ai...")
            os.environ["FAL_KEY"] = FAL_KEY
           
            image_url = fal_client.upload_file(CAMINHO_IMAGEM_TEMP)
            print(f"Upload concluído: {image_url}")
           
            print("IA gerando movimentos cósmicos... (Aguarde)")
            result = fal_client.subscribe(
                "fal-ai/kling-video/v1/standard/image-to-video",
                arguments={
                    "image_url": image_url,
                    "prompt": "Cinematic space movement, stars twinkling, slow camera zoom, realistic nebula motion",
                    "duration": "5",
                    "aspect_ratio": "16:9"
                }
            )
           
            video_url = result['video']['url']
            print(f"Vídeo gerado com sucesso! Link: {video_url}")
 
            response = requests.get(video_url, stream=True)
            with open(NOME_VIDEO_OUTPUT, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                f.flush()
                os.fsync(f.fileno())
 
            caminho_abs = os.path.abspath(NOME_VIDEO_OUTPUT)
 
            def finalizar_na_ui():
                global janela_player_global
                print("Renderizando player na nova janela...")
                janela_player_global = JanelaVideo(caminho_abs)
                janela_player_global.show()
                os.startfile(caminho_abs)
 
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(500, finalizar_na_ui)
 
        except Exception as e:
            print(f"ERRO CRÍTICO NA GERAÇÃO: {str(e)}")
 
            def erro_ui():
                QMessageBox.critical(janela, "Erro na IA", f"Não foi possível gerar o vídeo.\nDetalhe: {str(e)}")
            QTimer.singleShot(0, erro_ui)
 
    threading.Thread(target=thread_video, daemon=True).start()
    QMessageBox.information(janela, "Kling IA Ativada",
                            "A IA está criando um vídeo de 5 segundos!\n\n"
                            "Devido à alta qualidade, isso pode levar de 1 a 2 minutos.\n"
                            "Uma janela separada abrirá assim que estiver pronto.")
def reproduzir_voz():
    texto = descricao_box.toPlainText()
    if not texto or "PROCESSANDO" in texto: return
   
    texto_para_falar = texto.split("HISTÓRIA E ANÁLISE DA IA")[-1] if "HISTÓRIA E ANÁLISE DA IA" in texto else texto
 
    def thread_audio():
        try:
            VOICE = "pt-BR-FranciscaNeural"
            arquivo_audio = "temp_audio.mp3"
            async def generate():
                communicate = edge_tts.Communicate(texto_para_falar, VOICE)
                await communicate.save(arquivo_audio)
            asyncio.run(generate())
            pygame.mixer.music.load(arquivo_audio)
            pygame.mixer.music.play()
        except Exception as e: print(f"Erro áudio: {e}")
 
    threading.Thread(target=thread_audio, daemon=True).start()
 
def carregar_conteudo():
    pygame.mixer.music.stop()
    data_str = calendario.date().toString("yyyy-MM-dd")
    api_key = NASA_API_KEY if NASA_API_KEY else "DEMO_KEY"
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&date={data_str}"
 
    titulo_label.setText("CONECTANDO...")
    descricao_box.setPlainText("PROCESSANDO...")
    stack.setCurrentIndex(0)
    QApplication.processEvents()
 
    try:
        response = requests.get(url, timeout=10)
        res = response.json()
       
        titulo_en = res.get('title', 'No Title')
        expl_en = res.get('explanation', 'No explanation')
        titulo_pt = traduzir_texto(titulo_en)
        expl_pt = traduzir_texto(expl_en)
        media_url = res.get('url', '')
        media_type = res.get('media_type', '')
 
        titulo_label.setText(f"{titulo_pt.upper()}\n({titulo_en.upper()})")
 
        if media_type == 'image':
            img_data = requests.get(media_url).content
            with open(CAMINHO_IMAGEM_TEMP, "wb") as f:
                f.write(img_data)
 
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)
            imagem_label.setPixmap(pixmap.scaled(700, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
           
            relatorio_ia = gerar_relatorio_ia(expl_en)
           
            texto_final = "TEXTO ORIGINAL (INGLÊS)\n\n"
            texto_final += f"{expl_en}\n\n"
            texto_final += "TRADUÇÃO (PORTUGUÊS)\n\n"
            texto_final += f"{expl_pt}\n\n"
            texto_final += "HISTÓRIA E ANÁLISE DA IA\n\n"
            texto_final += f"{relatorio_ia}"
           
        elif media_type == 'video':
            stack.setCurrentIndex(1)
            video_view.setUrl(QUrl(media_url))
            texto_final = f"CONTEÚDO EM VÍDEO ORIGINAL DA NASA\n\nORIGINAL: {expl_en}\n\nTRADUÇÃO: {expl_pt}"
 
        descricao_box.setPlainText(texto_final)
        descricao_box.verticalScrollBar().setValue(0)
       
    except Exception as e:
        descricao_box.setPlainText(f"ERRO: {str(e)}")
 
app = QApplication(sys.argv)
janela = QWidget()
janela.setWindowTitle("NASA IA EXPLORER 2026 - PYTHON 3.14")
janela.resize(900, 950)
layout = QVBoxLayout()
 
nav = QHBoxLayout()
btn_ant = QPushButton("ANTERIOR")
btn_prox = QPushButton("PRÓXIMO")
calendario = QDateEdit(QDate.currentDate())
calendario.setCalendarPopup(True)
nav.addWidget(btn_ant)
nav.addWidget(calendario)
nav.addWidget(btn_prox)
 
btn_go = QPushButton("BUSCAR NA NASA")
btn_go.setStyleSheet("background: #0B3D91; color: white; font-weight: bold; height: 40px;")
 
titulo_label = QLabel("NASA APOD")
titulo_label.setAlignment(Qt.AlignCenter)
 
stack = QStackedWidget()
imagem_label = QLabel()
imagem_label.setAlignment(Qt.AlignCenter)
video_view = QWebEngineView()
stack.addWidget(imagem_label)
stack.addWidget(video_view)
 
descricao_box = QTextEdit()
descricao_box.setReadOnly(True)
 
botoes = QHBoxLayout()
btn_play = QPushButton("OUVIR")
btn_stop = QPushButton("PARAR")
btn_vid = QPushButton("GERAR VÍDEO 5s (KLING IA)")
btn_vid.setStyleSheet("background: #8E44AD; color: white; font-weight: bold; height: 40px;")
 
botoes.addWidget(btn_play)
botoes.addWidget(btn_stop)
botoes.addWidget(btn_vid)
 
layout.addLayout(nav)
layout.addWidget(btn_go)
layout.addWidget(titulo_label)
layout.addWidget(stack)
layout.addWidget(descricao_box)
layout.addLayout(botoes)
 
janela.setLayout(layout)
 
btn_go.clicked.connect(carregar_conteudo)
btn_vid.clicked.connect(gerar_video_ia_real)
btn_play.clicked.connect(reproduzir_voz)
btn_stop.clicked.connect(lambda: pygame.mixer.music.stop())
btn_ant.clicked.connect(lambda: calendario.setDate(calendario.date().addDays(-1)))
btn_prox.clicked.connect(lambda: calendario.setDate(calendario.date().addDays(1)))
 
janela.show()
sys.exit(app.exec_())