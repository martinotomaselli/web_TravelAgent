#  Web Travel Agent - Frontend

Questo è il frontend del progetto **RagsAI - Travel Agent**, una piattaforma web moderna che consente agli utenti di interagire con un assistente virtuale intelligente per ricevere suggerimenti di viaggio personalizzati.

##  Tech Stack

- **Laravel 11** + **Livewire** per la gestione delle interazioni in tempo reale
- **PHP 8.3**
- **Tailwind CSS** per uno stile moderno e responsive
- **AI Backend** (FastAPI + LLM) integrato via API

##  Funzionalità

- Chat AI interattiva in tempo reale
- Cambio lingua dinamico: 🇮🇹 Italiano, 🇬🇧 Inglese, 🇪🇸 Spagnolo
- Rilevamento automatico della lingua scritta dall’utente
- Risposte turistiche personalizzate e precise
- UI moderna e accessibile

##  Struttura principale
web_travelAgent/
├── app/
├── resources/
│ └── views/ # Template Blade Livewire
├── routes/
│ └── web.php # Rotte principali
├── app/Livewire/
│ └── Chatbot.php # Componente AI Livewire
├── public/
└── ...


##  AI Backend

Il progetto si interfaccia con un backend AI personalizzato creato con **FastAPI + Llama/ChatGPT**, ospitato separatamente in `ai/main.py`.  
Le richieste vengono inviate a `http://127.0.0.1:8001/chat/memory`.

## ⚙️ Setup

1. Clona il progetto:
   bash
   git clone https://github.com/tuo-utente/web_travelAgent.git
   cd web_travelAgent

   ## Installa le dipendenze:
composer install
npm install && npm run build

php artisan serve


cd ai
 uvicorn main:app --reload --port 8001
