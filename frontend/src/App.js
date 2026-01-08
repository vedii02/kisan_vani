import React, { useState, useRef } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';

export default function App() {
  const [isListening, setIsListening] = useState(false);
  const [text, setText] = useState('');
  const [messages, setMessages] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState('hi-IN');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const audioRef = useRef(new Audio());
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  const languages = [
    { code: 'hi-IN', name: 'हिंदी (Hindi)', flag: '🇮🇳' },
    { code: 'en-US', name: 'English', flag: '🇺🇸' },
    { code: 'mr-IN', name: 'मराठी (Marathi)', flag: '🇮🇳' },
    { code: 'gu-IN', name: 'ગુજરાતી (Gujarati)', flag: '🇮🇳' },
    { code: 'bn-IN', name: 'বাংলা (Bengali)', flag: '🇮🇳' },
    { code: 'te-IN', name: 'తెలుగు (Telugu)', flag: '🇮🇳' },
    { code: 'ta-IN', name: 'தமிழ் (Tamil)', flag: '🇮🇳' },
    { code: 'kn-IN', name: 'ಕನ್ನಡ (Kannada)', flag: '🇮🇳' },
    { code: 'ml-IN', name: 'മലയാളം (Malayalam)', flag: '🇮🇳' },
    { code: 'pa-IN', name: 'ਪੰਜਾਬੀ (Punjabi)', flag: '🇮🇳' }
  ];

  // Start Recording
  const startListening = async () => {
    try {
      console.log('🎤 Requesting microphone access...');
      
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 48000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          volume: 1.0
        }
      });

      streamRef.current = stream;
      console.log('✅ Microphone access granted');

      // Use best available format for Google STT
      let mimeType;
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        mimeType = 'audio/webm';
      } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
        mimeType = 'audio/ogg;codecs=opus';
      } else {
        mimeType = 'audio/ogg';
      }

      console.log('📼 Using MIME type:', mimeType);

      const mediaRecorder = new MediaRecorder(stream, { 
        mimeType,
        audioBitsPerSecond: 128000 // Higher quality
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          console.log('📦 Audio chunk:', e.data.size, 'bytes');
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        console.log('🛑 Recording stopped');
        console.log('📦 Total chunks:', audioChunksRef.current.length);
        
        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => {
            track.stop();
            console.log('🔌 Track stopped:', track.kind);
          });
          streamRef.current = null;
        }
        
        if (audioChunksRef.current.length === 0) {
          alert('❌ No audio recorded. Please try again.');
          return;
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        console.log('🎵 Audio blob size:', audioBlob.size, 'bytes');
        console.log('🎵 Audio MIME type:', audioBlob.type);

        if (audioBlob.size < 5000) {
          alert('⚠️ Audio too short. Please speak louder and for at least 3 seconds.');
          return;
        }

        // Convert to base64 and send
        const base64Audio = await blobToBase64(audioBlob);
        await processVoiceMessage(base64Audio);
      };

      // Start recording (collect chunks every 250ms for better quality)
      mediaRecorder.start(250);
      setIsListening(true);
      console.log('🔴 Recording started - Speak now!');

    } catch (err) {
      console.error('❌ Microphone error:', err);
      if (err.name === 'NotAllowedError') {
        alert('🎤 Microphone permission denied. Please allow microphone access.');
      } else if (err.name === 'NotFoundError') {
        alert('🎤 No microphone found. Please connect a microphone.');
      } else {
        alert(`❌ Error: ${err.message}`);
      }
    }
  };

  // Stop Recording
  const stopListening = () => {
    const recorder = mediaRecorderRef.current;
    
    if (!recorder) {
      console.log('⚠️ No active recorder');
      return;
    }

    if (recorder.state === 'recording') {
      console.log('🛑 Stopping recorder...');
      recorder.stop();
      setIsListening(false);
    } else {
      console.log('⚠️ Recorder not in recording state:', recorder.state);
    }
  };

  // Process Voice: STT → Chat → TTS
  const processVoiceMessage = async (audioBase64) => {
  try {
    setIsProcessing(true);

    const sttRes = await fetch('http://localhost:8000/voice/stt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio: audioBase64,
        language: selectedLanguage
      })
    });

    if (!sttRes.ok) throw new Error('STT failed');

    const sttData = await sttRes.json();

    if (!sttData.text || !sttData.text.trim()) {
      alert('Could not understand speech');
      return;
    }

    // ✅ ONLY fill textarea
    setText(sttData.text);

  } catch (err) {
    console.error(err);
    alert(err.message);
  } finally {
    setIsProcessing(false);
  }
};


  // Manual Text Send
  const sendMessage = async () => {
    if (!text.trim()) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    const messageText = text;
    setText('');
    setIsProcessing(true);

    try {
      const res = await fetch('http://localhost:8000/voice/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          language: selectedLanguage,
          farmer_id: 'farmer_123',
          farmer_name: 'Ramesh Kumar'
        })
      });

      const data = await res.json();
      const aiMsg = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, aiMsg]);

      if (data.audio) {
        playAudio(data.audio);
      }

    } catch (err) {
      console.error(err);
      alert('Failed to send message');
    } finally {
      setIsProcessing(false);
    }
  };

  // Play Audio
  const playAudio = (base64Audio) => {
    try {
      setIsSpeaking(true);
      const audioBlob = base64ToBlob(base64Audio, 'audio/mp3');
      const audioUrl = URL.createObjectURL(audioBlob);
      
      audioRef.current.src = audioUrl;
      audioRef.current.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };
      audioRef.current.onerror = (e) => {
        console.error('Audio play error:', e);
        setIsSpeaking(false);
      };
      audioRef.current.play().catch(err => {
        console.error('Play failed:', err);
        setIsSpeaking(false);
      });
      console.log('▶️ Audio playing');
    } catch (err) {
      console.error('Audio play error:', err);
      setIsSpeaking(false);
    }
  };

  // Helpers
  const blobToBase64 = (blob) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result.split(',')[1];
        console.log('✅ Converted to base64, length:', base64.length);
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });

  const base64ToBlob = (b64, mime) => {
    const bytes = atob(b64);
    const arr = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
    return new Blob([arr], { type: mime });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 p-6 flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-8 text-green-700">KisanAI 🌾</h1>

      {/* Voice Button */}
      <div className="flex flex-col items-center gap-4 mb-6">
        <button
          onClick={isListening ? stopListening : startListening}
          disabled={isProcessing}
          className={`w-20 h-20 rounded-full flex items-center justify-center text-white shadow-xl transition-all ${
            isListening 
              ? 'bg-red-500 animate-pulse scale-110' 
              : isProcessing
              ? 'bg-gray-400'
              : 'bg-green-500 hover:scale-110 hover:shadow-2xl'
          }`}
        >
          {isListening ? <MicOff size={32} /> : <Mic size={32} />}
        </button>

        {isListening && (
          <p className="text-red-600 font-bold animate-pulse">
            🔴 Recording... Click to stop
          </p>
        )}

        {isProcessing && (
          <p className="text-blue-600 font-bold">
            ⏳ Processing...
          </p>
        )}

        {isSpeaking && (
          <div className="flex items-center gap-2 text-purple-600 font-bold">
            <Volume2 className="animate-pulse" />
            Speaking...
          </div>
        )}

        <select
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value)}
          className="px-6 py-3 rounded-lg border-2 border-green-300 text-lg font-semibold"
          disabled={isListening || isProcessing}
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.flag} {lang.name}
            </option>
          ))}
        </select>
      </div>

      {/* Text Input */}
      <div className="w-full max-w-2xl mb-6">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Or type your message here..."
          className="w-full p-4 border-2 border-green-200 rounded-xl text-lg resize-none"
          rows={3}
        />
        <button
          onClick={sendMessage}
          disabled={isProcessing || !text.trim()}
          className="mt-2 w-full bg-green-500 text-white px-6 py-3 rounded-xl hover:bg-green-600 disabled:bg-gray-300 font-bold"
        >
          Send Message
        </button>
      </div>

      {/* Messages */}
      <div className="w-full max-w-2xl flex flex-col gap-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-xl shadow-md ${
              msg.role === 'user'
                ? 'bg-purple-100 self-end max-w-[80%]'
                : 'bg-green-100 self-start max-w-[80%]'
            }`}
          >
            <div className="font-bold text-sm mb-1">
              {msg.role === 'user' ? '👨‍🌾 You' : '🤖 KisanAI'}
            </div>
            <div className="text-lg">{msg.content}</div>
          </div>
        ))}
      </div>
    </div>
  );
}