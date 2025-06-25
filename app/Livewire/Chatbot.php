<?php

namespace App\Livewire;

use Livewire\Component;
use Illuminate\Support\Facades\Http;

class Chatbot extends Component
{

    public $currentMessage = '';
    public $userPrompt = '';
    public $chatMessages = [];
    public bool $useMemory = false;

    protected $rules = [
        'currentMessage' => 'required'
    ];

    protected $messages = [
        'currentMessage.required' => 'Please enter a message'
    ];

    public function ask()
    {
        $this->validate();

        $this->chatMessages[] = [
            'type' => 'human',
            'content' => $this->currentMessage
        ];

        $this->userPrompt = $this->currentMessage;

        $this->currentMessage = '';

        $this->js('$wire.generateResponse');
    }


public function generateResponse(): void
{
    
    //   Chiamo l’API FastAPI decidendo se usare memoria o meno
    
    $endpoint = $this->useMemory ? 'chat/memory' : 'ask';

    $payload = $this->useMemory
        ? [
        'session_id' => 'user-123',
        'messages'   => $this->chatMessages,
        'question'   => $this->userPrompt,
        'lang'       => $this->lang, 
    ]
    : [
        'question' => $this->userPrompt,
        'lang'     => $this->lang, 
    ];

    $response = Http::timeout(30)->post(
        rtrim(env('AI_API_URL', 'http://127.0.0.1:8001'), '/') . '/' . $endpoint,
        $payload
    );

    // Se la chiamata fallisce
    if ($response->failed()) {
        $this->chatMessages[] = [
            'type'    => 'ai',
            'content' => '🚨 AI non raggiungibile',
        ];
        return;
    }

    // Estraggo il JSON
    $data = $response->json();
    $this->chatMessages = $data['messages'] ?? $this->chatMessages;

    // Decido la risposta del bot
    $botReply = $data['answer']
        ?? '🤖 Nessuna risposta dal modello';

    // Aggiungo la risposta del bot alla chat
    $this->chatMessages[] = [
        'type'    => 'ai',
        'content' => $botReply,
    ];
    $prompt_lang = match ($this->lang) {
        'es' => 'Responde en español.',
        'en' => 'Answer in English.',
        default => 'Rispondi in italiano.',
    };

}

    public function render()
    {
        return view('livewire.chatbot');
    }

    public function updatedCurrentMessage()
    {
        $this->validateOnly('currentMessage');
    }

    public string $lang = 'it'; // lingua predefinita

public function switchLang()
{
    $this->lang = match ($this->lang) {
        'it' => 'en',
        'en' => 'es',
        default => 'it',
    };
    $this->chatMessages[] = [
        'type' => 'ai',
        'content' => match ($this->lang) {
            'it' => 'Lingua cambiata in Italiano.',
            'en' => 'Language changed to English.',
            'es' => 'Idioma cambiado a Español.',
        },
    ];
    
}

}

