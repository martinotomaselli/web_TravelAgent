<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ChatController extends Controller
{
    public function index()
    {
        return view('index');
    }

    public function ask(Request $request)
    {
        $request->validate([
            'question' => 'required|string',
        ]);

        $apiUrl = env('AI_API_URL');

        $response = Http::post($apiUrl, [
            'question' => $request->input('question'),
        ]);

        if ($response->failed()) {
            return response()->json([
                'error' => 'AI service unavailable',
            ], 502);
        }

        return $response->json(); // {"answer": "..."}
    }





}
