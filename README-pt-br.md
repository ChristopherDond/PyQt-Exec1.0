[English version](README.md)

<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/0/0a/Python.svg" width="70" alt="Python Logo" />

# ⚡ PyQt Exec 1.0

**Seis exercícios práticos de desktop com PyQt5 — de formulários simples a exploradores espaciais com IA.**

Uma jornada de aprendizado progressiva pelo desenvolvimento de GUIs em Python, APIs externas e inteligência artificial.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![NASA API](https://img.shields.io/badge/NASA-APOD%20API-0B3D91?style=flat-square)](https://api.nasa.gov/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](./LICENSE)

</div>

---

## ✨ Sobre

**PyQt Exec 1.0** é uma coleção de seis exercícios progressivos de aplicações desktop construídos em Python com PyQt5. Cada exercício explora uma nova camada do desenvolvimento de GUIs — começando pelo básico de formulários e requisições a APIs, e evoluindo para aplicativos completos alimentados pela API da NASA, modelos de linguagem de IA, conversão de texto em fala e até geração de vídeo com IA.

---

## 📁 Estrutura do Projeto

```
PyQt-Exec1.0/
│
├── PyQt1_0.py        # Exercício 1 — Formulário completo de cadastro com auto-preenchimento ViaCEP
├── PyQt2_0.py        # Exercício 2 — Consulta simples de CEP (ViaCEP)
├── PyQt3_0.py        # Exercício 3 — Verificador de preço de criptomoedas (API CoinGecko)
├── PyQt4_0.py        # Exercício 4 — Explorador NASA APOD com análise IA Gemini
├── PyQt5_0.py        # Exercício 5 — Explorador NASA + IA Groq + TTS + vídeo Kling AI
├── PyQt6_0.py        # Exercício 6 — Explorador NASA completo com vídeo AnimateDiff local
│
├── .env              # Chaves de API (NASA, Gemini, Groq, Fal.ai) — não versionado
├── requirements.txt  # Dependências do projeto
└── README.md
```

---

## 🧪 Exercícios

### `PyQt1_0.py` — Formulário de Cadastro com Auto-preenchimento ViaCEP
> *Um formulário completo de cadastro de dados pessoais.*

Interface de cadastro completa com inputs estilizados, máscaras de entrada para CPF, RG e CEP, seletor de data e seletor de estado (ComboBox de UF). Ao digitar o CEP, ele consulta automaticamente a **API ViaCEP** e preenche rua, bairro, cidade e estado. Inclui validação de campos com listagem de erros e botão de limpar/redefinir.

**Conceitos-chave:** máscaras de entrada do `QLineEdit`, `QDateEdit`, `QComboBox`, `QMessageBox`, sinal `editingFinished`, API REST ViaCEP, validação de formulários, theming via stylesheet.

---

### `PyQt2_0.py` — Consulta Simples de CEP
> *Uma ferramenta mínima de busca de endereço usando a API ViaCEP.*

A versão mais simples do conceito de consulta de CEP — uma janela leve com campo de CEP mascarado, botão de busca e campos de resultado somente leitura para rua, bairro, cidade e estado. Serve como protótipo fundamental antes do formulário completo do Exercício 1.

**Conceitos-chave:** `QLineEdit`, `setEnabled(False)` para campos somente leitura, `QMessageBox`, chamada básica à API ViaCEP, `setInputMask`.

---

### `PyQt3_0.py` — Verificador de Preço de Criptomoedas
> *Uma ferramenta de busca de preço de criptomoedas em tempo real.*

Digite o nome de qualquer criptomoeda (ex.: `bitcoin`, `ethereum`) e busque preços ao vivo em **BRL** e **USD** via **API CoinGecko**. Inclui feedback dinâmico de cor no label (azul para sucesso, vermelho/laranja para erros) e estado de carregamento enquanto a requisição está em andamento.

**Conceitos-chave:** `QLabel`, `QLineEdit`, `QPushButton`, `processEvents()` para responsividade da UI, API REST CoinGecko, tratamento de erros com feedback visual.

---

### `PyQt4_0.py` — Explorador NASA APOD + IA Gemini
> *Navegue pela Astronomy Picture of the Day da NASA com relatórios científicos gerados por IA.*

Navegação por data para explorar qualquer registro do APOD, com tradução automática (EN → PT) via `deep_translator`. As imagens são exibidas inline; vídeos carregam via `QWebEngineView`. Cada imagem é analisada pelo **Google Gemini 2.0 Flash**, que gera um relatório científico em português. Inclui opção de salvar a imagem atual em disco.

**Conceitos-chave:** `QStackedWidget`, `QWebEngineView`, `QFileDialog`, `QDateEdit`, `QPixmap`, API NASA APOD, `deep_translator`, `google.generativeai` (Gemini), PIL para decodificação de imagens, segredos no `.env`.

---

### `PyQt5_0.py` — Explorador NASA + IA Groq + TTS + Vídeo Kling AI
> *Um explorador NASA cheio de recursos com narração por voz e geração de vídeo com IA.*

Baseia-se no Exercício 4 com melhorias significativas: os relatórios de IA agora são gerados pelo **LLaMA 3.1** via **Groq**; um mecanismo de texto para fala (`edge_tts` + `pygame`) lê o conteúdo em voz alta em português brasileiro; e um botão dedicado aciona o **Kling AI** (via `fal.ai`) para gerar um **vídeo cinematográfico de 5 segundos** a partir da imagem da NASA, exibido em uma janela separada de player de vídeo. Todas as operações pesadas rodam em threads de segundo plano para manter a interface responsiva.

**Conceitos-chave:** `threading`, `asyncio`, `edge_tts`, `pygame.mixer`, `fal_client`, SDK Groq, `QTimer.singleShot` para atualizações de UI thread-safe, `QMessageBox`, widget customizado `JanelaVideo` com player HTML5 embutido.

---

### `PyQt6_0.py` — Explorador NASA Completo com Vídeo AnimateDiff Local
> *O exercício mais completo — um aplicativo de pesquisa NASA polido com múltiplas abas e geração de vídeo com IA local.*

Um explorador NASA totalmente reestruturado com sistema de busca duplo: **APOD por data** e busca por texto livre via **API NASA Images** com resultados em dropdown. O conteúdo é exibido em três abas — Inglês, Português e Análise de IA. As imagens são aprimoradas com PIL (auto-contraste + nitidez). O TTS suporta múltiplas vozes por idioma. A geração de vídeo roda **localmente** usando **AnimateDiff + Stable Diffusion**, com detecção automática de GPU/CPU via PyTorch. Inclui salvamento de imagens em disco e um código mais limpo e modular.

**Conceitos-chave:** `QTabWidget`, `QComboBox` com dados `UserRole`, `QProgressDialog`, `QFileDialog`, `diffusers` (pipeline AnimateDiff), `torch` (CUDA/CPU), `ImageEnhance` / `ImageOps` (PIL), API NASA Images, Groq + LLaMA, `edge_tts`, `pygame`, design de funções totalmente modular.

---

## 🛠️ Tecnologias

| Categoria | Bibliotecas / Ferramentas |
|-----------|---------------------------|
| GUI | PyQt5 |
| Requisições HTTP | `requests` |
| Tradução | `deep_translator` (Google Translate) |
| Texto para Fala | `edge_tts`, `pygame` |
| IA — Nuvem | Google Gemini 2.0 Flash, Groq (LLaMA 3.1) |
| IA — Vídeo (nuvem) | Kling AI via `fal_client` |
| IA — Vídeo (local) | `diffusers` AnimateDiff + Stable Diffusion |
| Processamento de Imagem | `Pillow` (PIL) |
| APIs | ViaCEP, CoinGecko, NASA APOD, NASA Images |
| Configuração | `python-dotenv` |

---

## 📦 Como Começar

### Pré-requisitos

- Python 3.8+
- pip

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/ChristopherDond/PyQt-Exec1.0.git
cd PyQt-Exec1.0

# 2. (Recomendado) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows

# 3. Instale as dependências
pip install -r requirements.txt
```

### Variáveis de Ambiente

Para os exercícios 4, 5 e 6, crie um arquivo `.env` na raiz do projeto:

```env
NASA_API_KEY=your_nasa_api_key
GEMINI_API_KEY=your_gemini_api_key     # Somente Exercício 4
GROQ_API_KEY=your_groq_api_key         # Exercícios 5 e 6
FAL_KEY=your_fal_api_key               # Somente Exercício 5
```

> 💡 Chaves de API gratuitas: [NASA](https://api.nasa.gov/) · [Gemini](https://aistudio.google.com/) · [Groq](https://console.groq.com/) · [Fal.ai](https://fal.ai/)

### Executando qualquer exercício

```bash
python PyQt1_0.py   # ou PyQt2_0.py, PyQt3_0.py, etc.
```

---

## 📈 Progressão de Aprendizado

```
PyQt2  →  PyQt1  →  PyQt3  →  PyQt4  →  PyQt5  →  PyQt6
Basic      Forms    Live       NASA       NASA +     Full
CEP        +Masks   Crypto     + Gemini   TTS +      App +
Lookup     +Style   Prices     Reports    Kling AI   Local AI
```

Cada exercício é construído intencionalmente sobre o anterior — novos widgets, novas APIs, threading mais complexo e experiências de usuário progressivamente mais ricas.

---

## 🤝 Contribuindo

1. Faça um fork do repositório
2. Crie uma branch de feature: `git checkout -b feature/sua-ideia`
3. Faça commit: `git commit -m "feat: descreva sua alteração"`
4. Envie: `git push origin feature/sua-ideia`
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](./LICENSE).

---

<div align="center">

Feito com 🐍 ☕ e muito `app.exec_()` por [ChristopherDond](https://github.com/ChristopherDond)

</div>
