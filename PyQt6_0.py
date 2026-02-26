import sys
import requests
import os
import threading
import asyncio
import edge_tts
import shutil
import torch
import pygame
import webbrowser
from dotenv import load_dotenv
from groq import Groq
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QPushButton, QTextEdit, QDateEdit, QLineEdit,
                             QHBoxLayout, QMessageBox, QComboBox, QTabWidget, 
                             QFileDialog, QProgressDialog)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDate
from deep_translator import GoogleTranslator
from PIL import Image, ImageEnhance, ImageOps
from diffusers import AnimateDiffPipeline, MotionAdapter, DPMSolverMultistepScheduler
from diffusers.utils import export_to_video

load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

pygame.mixer.init()

IMG_TEMP = "temp_nasa_image.jpg"
VID_TEMP = "temp_ia_video.mp4"

data_store = {
    'en_title': '', 'pt_title': '', 'en_expl': '',
    'pt_expl': '', 'ia_report': '', 'url': ''
}

def traduzir(texto):
    try:
        return GoogleTranslator(source='auto', target='pt').translate(texto) if texto else ""
    except:
        return "Erro na tradução."

def gerar_relatorio_ia(descricao):
    try:
        prompt = f"Gere um relatório detalhado em PORTUGUÊS-BR sobre: {descricao}. Use títulos em MAIÚSCULAS e sem Markdown."
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except:
        return "Erro ao gerar análise da IA."

def processar_imagem(conteudo):
    with open(IMG_TEMP, "wb") as f:
        f.write(conteudo)
    try:
        with Image.open(IMG_TEMP) as img:
            img = ImageOps.autocontrast(img.convert("RGB"))
            img = ImageEnhance.Sharpness(img).enhance(1.6)
            img.save(IMG_TEMP, quality=95)
    except Exception as e:
        print(f"Erro imagem: {e}")

def tocar_audio(texto, voz, botao):
    if not texto or len(texto) < 5: return
    texto_original = botao.text()
    botao.setText("GERANDO ÁUDIO...")
    def _run():
        try:
            arquivo = f"temp_audio_{voz[:2]}.mp3"
            async def _gen():
                await edge_tts.Communicate(texto[:2500], voz).save(arquivo)
            asyncio.run(_gen())
            pygame.mixer.music.load(arquivo)
            pygame.mixer.music.play()
        except: pass
        finally:
            botao.setText(texto_original)
    threading.Thread(target=_run, daemon=True).start()

def exibir_conteudo(url, titulo, expl):
    if not url: return
    lbl_titulo.setText("BUSCANDO...")
    try:
        res = requests.get(url, timeout=15)
        processar_imagem(res.content)
        
        data_store.update({
            'en_title': titulo, 'en_expl': expl,
            'pt_title': traduzir(titulo), 'pt_expl': traduzir(expl),
            'ia_report': gerar_relatorio_ia(expl), 'url': url
        })

        lbl_titulo.setText(f"{data_store['pt_title'].upper()}\n({titulo.upper()})")
        lbl_img.setPixmap(QPixmap(IMG_TEMP).scaled(lbl_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        txt_en.setPlainText(f"{data_store['en_title']}\n\n{data_store['en_expl']}")
        txt_pt.setPlainText(f"{data_store['pt_title']}\n\n{data_store['pt_expl']}")
        txt_ia.setPlainText(data_store['ia_report'])
        tabs.setCurrentIndex(0)
    except Exception as e:
        QMessageBox.critical(None, "Erro", str(e))

def buscar_keyword():
    termo = edit_busca.text()
    if not termo: return
    
    lbl_titulo.setText("BUSCANDO...")
    combo_res.clear()
    try:
        res = requests.get(f"https://images-api.nasa.gov/search?q={termo}&media_type=image").json()
        itens = res.get('collection', {}).get('items', [])[:15]
        
        if not itens:
            lbl_titulo.setText("NADA ENCONTRADO")
            return

        combo_res.addItem(f"🔍 {len(itens)} resultados...")
        for i in itens:
            d = i['data'][0]
            link = i['links'][0]['href'] if i.get('links') else None
            combo_res.addItem("⭐ " + d.get('title', 'Sem título'))
            combo_res.setItemData(combo_res.count()-1, {"url": link, "title": d.get('title'), "expl": d.get('description')}, Qt.UserRole)
        
        combo_res.show()
        combo_res.showPopup()
        lbl_titulo.setText("NASA EXPLORER")
    except:
        lbl_titulo.setText("ERRO NA BUSCA")

def buscar_apod():
    data_str = edit_data.date().toString("yyyy-MM-dd")
    lbl_titulo.setText("BUSCANDO...")
    try:
        res = requests.get(f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={data_str}").json()
        if 'url' in res:
            exibir_conteudo(res.get('url'), res.get('title'), res.get('explanation'))
            combo_res.hide()
    except Exception as e:
        lbl_titulo.setText("ERRO NA BUSCA")
        QMessageBox.critical(None, "Erro", str(e))

def salvar_img():
    if not os.path.exists(IMG_TEMP): return
    path, _ = QFileDialog.getSaveFileName(None, "Salvar", "", "JPEG (*.jpg);;PNG (*.png)")
    if path: shutil.copy(IMG_TEMP, path)

def gerar_vid():
    if not data_store['en_expl']: return
    prog = QProgressDialog("Gerando vídeo...", "Cancelar", 0, 0)
    prog.show()

    def _worker():
        try:
            dev = "cuda" if torch.cuda.is_available() else "cpu"
            typ = torch.float16 if dev == "cuda" else torch.float32
            
            adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2", torch_dtype=typ)
            pipe = AnimateDiffPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", motion_adapter=adapter, torch_dtype=typ)
            pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, algorithm_type="dpmsolver++", use_karras_sigmas=True)

            if dev == "cuda": pipe.enable_model_cpu_offload()
            else: pipe.to("cpu")

            out = pipe(prompt=f"Space, {data_store['en_expl'][:100]}", num_frames=16, num_inference_steps=15)
            export_to_video(out.frames[0], VID_TEMP, fps=8)
            webbrowser.open(VID_TEMP)
        except Exception as e: print(e)
        finally: prog.cancel()

    threading.Thread(target=_worker, daemon=True).start()

app = QApplication(sys.argv)
win = QWidget()
win.setWindowTitle("NASA EXPLORER")
win.resize(1200, 800)

main_layout = QVBoxLayout(win)
top_bar = QHBoxLayout()
edit_busca = QLineEdit(); edit_busca.setPlaceholderText("Pesquisar...")
btn_busca = QPushButton("PESQUISAR")
edit_data = QDateEdit(QDate.currentDate()); edit_data.setCalendarPopup(True)
edit_data.setMaximumDate(QDate.currentDate())
btn_apod = QPushButton("APOD")

for w in [edit_busca, btn_busca, edit_data, btn_apod]: top_bar.addWidget(w)
main_layout.addLayout(top_bar)

combo_res = QComboBox(); combo_res.hide()
main_layout.addWidget(combo_res)

lbl_titulo = QLabel("NASA EXPLORER")
lbl_titulo.setStyleSheet("font-weight: bold; background: #222; color: white; padding: 10px;")
lbl_titulo.setAlignment(Qt.AlignCenter)
main_layout.addWidget(lbl_titulo)

content_area = QHBoxLayout()
lbl_img = QLabel("Selecione um conteúdo...")
lbl_img.setStyleSheet("background: black; border: 1px solid #444;")
lbl_img.setMinimumSize(700, 500)
content_area.addWidget(lbl_img, 2)

tabs = QTabWidget()
def add_tab(name, color, voice):
    w = QWidget(); l = QVBoxLayout(w)
    txt = QTextEdit(); txt.setReadOnly(True)
    btn = QPushButton(f"OUVIR {name}")
    btn.setStyleSheet(f"background: {color}; color: white; font-weight: bold; padding: 8px;")
    btn.clicked.connect(lambda: tocar_audio(txt.toPlainText(), voice, btn))
    l.addWidget(txt); l.addWidget(btn)
    tabs.addTab(w, name)
    return txt

txt_en = add_tab("ENGLISH", "#2E86AB", "en-US-AriaNeural")
txt_pt = add_tab("PORTUGUÊS", "#A23B72", "pt-BR-FranciscaNeural")
txt_ia = add_tab("ANÁLISE IA", "#F18F01", "pt-BR-FranciscaNeural")

content_area.addWidget(tabs, 1)
main_layout.addLayout(content_area)

bot_bar = QHBoxLayout()
btn_stop = QPushButton("⏹ PARAR"); btn_save = QPushButton("💾 SALVAR"); btn_vid = QPushButton("🎬 VÍDEO")
btn_stop.clicked.connect(lambda: pygame.mixer.music.stop())
btn_save.clicked.connect(salvar_img)
btn_vid.clicked.connect(gerar_vid)

for b in [btn_stop, btn_save, btn_vid]: bot_bar.addWidget(b)
main_layout.addLayout(bot_bar)

btn_busca.clicked.connect(buscar_keyword)
edit_busca.returnPressed.connect(buscar_keyword)
btn_apod.clicked.connect(buscar_apod)
combo_res.currentIndexChanged.connect(lambda i: exibir_conteudo(combo_res.itemData(i)['url'], combo_res.itemData(i)['title'], combo_res.itemData(i)['expl']) if i>0 else None)

win.show()
sys.exit(app.exec_())