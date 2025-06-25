import os
import re
import uuid
import traceback
import wikipedia
wikipedia.set_lang("it")


from typing import Optional , List, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

from langdetect import detect


from fastapi.responses import JSONResponse

#  Configurazione 
# Carica le variabili d'ambiente da un file .env
load_dotenv()
OLLAMA_HOST  = os.getenv("OLLAMA_HOST",  "http://127.0.0.1:11434")
MODEL_NAME   = os.getenv("OLLAMA_MODEL", "llama3")

llm = ChatOllama(base_url=OLLAMA_HOST, model=MODEL_NAME)

# FastAPI 
app = FastAPI(
    title="Local LLM Tourist Assistant",
    version="1.0.0",
    description="API FastAPI + LangChain in locale con Ollama."
)
# Wikipedia API 
@app.get("/api/wiki")
def get_wiki_summary(query: str, lang: str = "en"):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return {"result": summary}
    except wikipedia.exceptions.DisambiguationError as e:
        return JSONResponse(status_code=400, content={"error": f"Query ambigua: {e.options}"})
    except wikipedia.exceptions.PageError:
        return JSONResponse(status_code=404, content={"error": "Nessuna pagina trovata."})
#  Memoria di sessione 
_sessions: Dict[str, ConversationBufferMemory] = {}

def get_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in _sessions:
        _sessions[session_id] = ConversationBufferMemory(
            memory_key="history",
            return_messages=True
        )
    return _sessions[session_id]

#  Modelli Pydantic 
class Msg(BaseModel):
    type: str = Field(examples=["human", "ai"])
    content: str

class ChatReq(BaseModel):
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Msg]
    model: Optional[str] = Field(default=MODEL_NAME)

class AskReq(BaseModel):
    question: str
    model: Optional[str] = MODEL_NAME

#  Endpoints 
@app.get("/ping")
def ping():
    return {"message": "ciao, sono un assistente turistico locale!"}

@app.get("/models")
def list_models():
    import requests
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
        return r.json()
    except Exception as exc:
        raise HTTPException(500, f"Ollama host error: {exc}")

#  Chat one-shot 
class Message(BaseModel):
    type: str
    content: str

class ChatReq(BaseModel):
    session_id: str
    messages: List[Message]
    lang: Optional[str] = None



@app.post("/ask")
def ask(req: AskReq):
    prompt = (
        "Sei un assistente turistico educato e preparato. "
        f"Rispondi in italiano alla seguente domanda:\nDOMANDA: {req.question}"
    )
    try:
        res = llm.invoke([HumanMessage(content=prompt)])
        return {"answer": res.content}
    except Exception as exc:
        print("ERRORE:", str(exc))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc))

#  Chat con memoria 
@app.post("/chat/memory")
def chat_with_memory(req: ChatReq):
    #  Recupera o crea memoria
    memory = get_memory(req.session_id)

    #  Aggiungi messaggi precedenti alla memoria
    for m in req.messages[:-1]:
        if m.type == "human":
            memory.chat_memory.add_message(HumanMessage(content=m.content))
        elif m.type in ("ai", "assistant", "bot"):
            memory.chat_memory.add_message(AIMessage(content=m.content))
        else:
            raise HTTPException(400, f"Tipo di messaggio non valido: {m.type}")

    #  Rileva lingua dell'ultimo messaggio utente
    last_user_input = req.messages[-1].content
    lang = req.lang if req.lang else detect(last_user_input)
   
    print("Lingua usata:", lang)

    

    #  Costruisci il prompt nella lingua corretta
    if lang == "es":
        prompt_lang = (
            "Eres una guía turística experta. Responde solo en español. "
            "Responde solo con las atracciones de esa ciudad. "
            "Si el usuario escribe en un idioma, responde en ese **mismo idioma**. "
            "No hagas introducciones ni saludos. "
            "Responde con un máximo de 5 puntos claros."
        )
    elif lang == "en":
        prompt_lang = (
            "You are an expert travel guide. Answer only in English. "
            "Reply only with the attractions of the given city. "
            "If the user writes in a language, reply in the **same language**. "
            "No introductions or greetings. "
            "Answer with a maximum of 5 clear bullet points."
        )
    else:
        prompt_lang = (
            "Sei una guida turistica esperta. Rispondi solo in italiano. "
            "Rispondi solo con le attrazioni di quella città. "
            "Se l'utente scrive in una lingua, rispondi nella **stessa lingua**. "
            "Non fare introduzioni né saluti. "
            "Rispondi con massimo 5 punti elenco chiari."
        )

    #  Crea il prompt con memoria
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_lang),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    #  Crea e invoca la conversazione
    conversation = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=memory
    )

    output = conversation.invoke({"input": last_user_input})

    return {"response": output}

    