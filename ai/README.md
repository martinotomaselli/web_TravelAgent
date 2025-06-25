# RagsAI – Travel Assistant con LLM, FastAPI e Laravel

**RagsAI** è un assistente virtuale turistico intelligente, progettato per rispondere alle domande degli utenti su città, monumenti e attrazioni in base alla lingua usata.  
Il progetto sfrutta LangChain, Ollama e FastAPI per la parte AI, e Laravel (con Livewire) per l’interfaccia frontend.

---

## 🔧 Tecnologie usate

- Laravel 11 + Livewire
- PHP 8.3
- Python 3.10
- FastAPI
- LangChain
- Ollama (con LLaMA3)
- Tailwind CSS



##  Funzionalità principali

-  Riconoscimento automatico della lingua (🇮🇹 🇬🇧 🇪🇸)
-  Cambio lingua manuale (pulsante nella chat)
-  Memoria conversazionale
-  Risposte in stile bullet points, chiare e brevi
-  Interfaccia moderna ispirata a ChatGPT



##  Modalità AI

Ogni messaggio viene analizzato in `main.py`, dove:

- Viene rilevata o ricevuta la lingua (`detect()` o `lang` da Laravel)
- Viene costruito un prompt in base alla lingua
- Viene invocata una conversazione LangChain tramite `ConversationChain`
- La risposta viene restituita e mostrata nella chat Laravel



##  Come eseguire il progetto

### 1. Avvia il backend AI (Python + FastAPI)


cd ai
ollama run llama3
 uvicorn main:app --reload --port 8001
