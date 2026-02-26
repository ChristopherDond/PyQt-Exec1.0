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
                             QPushButton, QTextEdit, QDateEdit, QLineEdit,
                             QHBoxLayout, QStackedWidget, QMessageBox, QListWidget, 
                             QFileDialog, QComboBox, QTabWidget, QFrame)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDate
from deep_translator import GoogleTranslator
import pygame
from PIL import Image, ImageEnhance, ImageOps

load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
pygame.mixer.init()

CAMINHO_IMAGEM_TEMP = "temp_nasa_image.jpg"

conteudo_atual = {
    'titulo_en': '', 'titulo_pt': '', 'expl_en': '',
    'expl_pt': '', 'relatorio_ia': '', 'url_imagem': ''
}

def salvar_imagem():
    if not os.path.exists(CAMINHO_IMAGEM_TEMP):
        QMessageBox.warning(janela, "Erro", "Não há imagem para salvar!")
        return
    caminho, _ = QFileDialog.getSaveFileName(janela, "Salvar Imagem", "", "JPEG (*.jpg);;PNG (*.png)")
    if caminho:
        try:
            shutil.copy(CAMINHO_IMAGEM_TEMP, caminho)
            QMessageBox.information(janela, "Sucesso", "Imagem salva com sucesso!")
        except Exception as e:
            QMessageBox.critical(janela, "Erro", f"Falha ao salvar: {e}")

def buscar_palavra_chave():
    termo = campo_pesquisa.text()
    if not termo: 
        combo_resultados.hide()
        return
    
    titulo_label.setText("BUSCANDO...")
    combo_resultados.clear()
    
    try:
        url = f"https://images-api.nasa.gov/search?q={termo}&media_type=image"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        itens = res.json().get('collection', {}).get('items', [])[:15]
        
        if not itens:
            combo_resultados.hide()
            titulo_label.setText("NENHUM RESULTADO ENCONTRADO")
            return
        
        combo_resultados.addItem(f"🔍 {len(itens)} resultados encontrados...")
        
        for i in itens:
            dados = i['data'][0]
            titulo = dados.get('title', 'Sem título')
            link_img = i['links'][0]['href']
            expl = dados.get('description', 'Sem descrição')
            
            combo_resultados.addItem("⭐ " + titulo)
            index = combo_resultados.count() - 1
            combo_resultados.setItemData(index, {"url": link_img, "title": titulo, "expl": expl}, Qt.UserRole)
        
        combo_resultados.show()
        combo_resultados.showPopup()
        
    except Exception as e:
        QMessageBox.critical(janela, "Erro de Conexão", f"Não foi possível buscar: {str(e)}")
        titulo_label.setText("ERRO NA BUSCA")

def carregar_da_combo(index):
    if index <= 0: return
    dados = combo_resultados.itemData(index, Qt.UserRole)
    if dados:
        exibir_conteudo_final(dados['url'], dados['title'], dados['expl'])

def atualizar_abas():
    aba_ingles.setPlainText(f"{conteudo_atual['titulo_en']}\n\n{conteudo_atual['expl_en']}")
    aba_portugues.setPlainText(f"{conteudo_atual['titulo_pt']}\n\n{conteudo_atual['expl_pt']}")
    aba_ia.setPlainText(conteudo_atual['relatorio_ia'])

def exibir_conteudo_final(url_media, titulo_en, expl_en):
    if not url_media:
        QMessageBox.warning(janela, "Aviso", "Este item não possui uma URL de imagem válida.")
        return

    try:
        titulo_pt = traduzir_texto(titulo_en)
        expl_pt = traduzir_texto(expl_en)
        relatorio_ia = gerar_relatorio_ia(expl_en)

        res = requests.get(url_media, timeout=15)
        res.raise_for_status()
        
        with open(CAMINHO_IMAGEM_TEMP, "wb") as f:
            f.write(res.content)
        
        try:
            with Image.open(CAMINHO_IMAGEM_TEMP) as img:
                img = img.convert("RGB")
                img = ImageOps.autocontrast(img)
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.6).save(CAMINHO_IMAGEM_TEMP, quality=95)
        except Exception as img_err:
            print(f"Erro ao processar filtros: {img_err}")

        # Atualiza Interface
        conteudo_atual.update({
            'titulo_en': titulo_en, 'expl_en': expl_en,
            'titulo_pt': titulo_pt, 'expl_pt': expl_pt,
            'relatorio_ia': relatorio_ia, 'url_imagem': url_media
        })

        titulo_label.setText(f"{titulo_pt.upper()}\n({titulo_en.upper()})")
        pixmap = QPixmap(CAMINHO_IMAGEM_TEMP)
        imagem_label.setPixmap(pixmap.scaled(imagem_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        imagem_label.setScaledContents(True)
        
        atualizar_abas()
        tabs_descricao.setCurrentIndex(0)
        
    except Exception as e:
        QMessageBox.critical(janela, "Erro", f"Falha ao carregar conteúdo: {str(e)}")

def traduzir_texto(texto):
    try:
        if not texto or texto == "No explanation": return "Sem descrição."
        return GoogleTranslator(source='auto', target='pt').translate(texto)
    except: return "Erro na tradução."

def gerar_relatorio_ia(descricao_nasa):
    try:
        prompt = f"Relatório detalhado em PT-BR (MAIÚSCULAS PARA TÍTULOS, SEM MARKDOWN): {descricao_nasa}"
        completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
        return completion.choices[0].message.content
    except: return "Erro ao gerar análise da IA."

def carregar_conteudo():
    data_selecionada = calendario.date()
    if data_selecionada > QDate.currentDate():
        QMessageBox.warning(janela, "Data Inválida", "A NASA ainda não viajou para o futuro! Selecione a data de hoje ou anterior.")
        return

    data_str = data_selecionada.toString("yyyy-MM-dd")
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={data_str}"
    try:
        res = requests.get(url, timeout=10).json()
        if 'url' in res:
            exibir_conteudo_final(res.get('url'), res.get('title'), res.get('explanation'))
            combo_resultados.hide()
        else:
            QMessageBox.information(janela, "Aviso", "Nenhum dado disponível para esta data.")
    except Exception as e: 
        QMessageBox.critical(janela, "Erro", f"Erro ao acessar APOD: {e}")

def tocar_audio(texto, lang_voice):
    if not texto or len(texto) < 5: return
    def thread_audio():
        try:
            arquivo = f"temp_audio_{lang_voice[:2]}.mp3"
            async def generate():
                comm = edge_tts.Communicate(texto[:1000], lang_voice)
                await comm.save(arquivo)
            asyncio.run(generate())
            pygame.mixer.music.load(arquivo)
            pygame.mixer.music.play()
        except Exception as e: print(f"Erro audio: {e}")
    threading.Thread(target=thread_audio, daemon=True).start()

app = QApplication(sys.argv)
janela = QWidget()
janela.setWindowTitle("NASA IA EXPLORER 2026")
janela.resize(1200, 800)

layout = QVBoxLayout()
linha_pesquisa = QHBoxLayout()
campo_pesquisa = QLineEdit()
campo_pesquisa.setPlaceholderText("Ex: Mars, Galaxy...")
btn_pesquisar = QPushButton("PESQUISAR")

calendario = QDateEdit(QDate.currentDate())
calendario.setCalendarPopup(True)
calendario.setMaximumDate(QDate.currentDate()) 

btn_apod = QPushButton("BUSCAR POR DATA")

linha_pesquisa.addWidget(campo_pesquisa)
linha_pesquisa.addWidget(btn_pesquisar)
linha_pesquisa.addSpacing(15)
linha_pesquisa.addWidget(calendario)
linha_pesquisa.addWidget(btn_apod)
layout.addLayout(linha_pesquisa)

combo_resultados = QComboBox()
combo_resultados.hide()
layout.addWidget(combo_resultados)

titulo_label = QLabel("NASA IA EXPLORER")
titulo_label.setAlignment(Qt.AlignCenter)
titulo_label.setStyleSheet("font-weight: bold; background-color: #222; color: #FFFFFF; padding: 10px; font-size: 14px;")
layout.addWidget(titulo_label)

area_central = QHBoxLayout()
imagem_label = QLabel("Selecione uma data ou pesquise...")
imagem_label.setAlignment(Qt.AlignCenter)
imagem_label.setStyleSheet("background-color: black; border: 1px solid #444;")
imagem_label.setMinimumSize(700, 550)
area_central.addWidget(imagem_label, 2)

tabs_descricao = QTabWidget()
aba_ingles = QTextEdit(); aba_ingles.setReadOnly(True)
aba_portugues = QTextEdit(); aba_portugues.setReadOnly(True)
aba_ia = QTextEdit(); aba_ia.setReadOnly(True)

def criar_aba(widget_texto, btn_text, cor, func_audio):
    w = QWidget(); l = QVBoxLayout()
    b = QPushButton(btn_text); b.setStyleSheet(f"background-color: {cor}; color: white; font-weight: bold; padding: 10px;")
    b.clicked.connect(func_audio)
    l.addWidget(widget_texto); l.addWidget(b); w.setLayout(l)
    return w

tabs_descricao.addTab(criar_aba(aba_ingles, "▶ OUVIR EN", "#2E86AB", lambda: tocar_audio(aba_ingles.toPlainText(), "en-US-AriaNeural")), "ENGLISH")
tabs_descricao.addTab(criar_aba(aba_portugues, "▶ OUVIR PT", "#A23B72", lambda: tocar_audio(aba_portugues.toPlainText(), "pt-BR-FranciscaNeural")), "PORTUGUÊS")
tabs_descricao.addTab(criar_aba(aba_ia, "▶ OUVIR IA", "#F18F01", lambda: tocar_audio(aba_ia.toPlainText(), "pt-BR-FranciscaNeural")), "ANÁLISE IA")

area_central.addWidget(tabs_descricao, 1)
layout.addLayout(area_central)

rodape = QHBoxLayout()
btn_stop = QPushButton("⏹ PARAR ÁUDIO"); btn_save = QPushButton("💾 SALVAR IMAGEM")
btn_stop.clicked.connect(lambda: pygame.mixer.music.stop())
btn_save.clicked.connect(salvar_imagem)
rodape.addWidget(btn_stop); rodape.addStretch(); rodape.addWidget(btn_save)
layout.addLayout(rodape)

janela.setLayout(layout)
btn_pesquisar.clicked.connect(buscar_palavra_chave)
campo_pesquisa.returnPressed.connect(buscar_palavra_chave)
combo_resultados.currentIndexChanged.connect(carregar_da_combo)
btn_apod.clicked.connect(carregar_conteudo)

janela.show()
sys.exit(app.exec_())