


// working code
import React, { useState, useRef } from "react";

const ChatPage = () => {
  const [chat, setChat] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [videoEnabled, setVideoEnabled] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // --- VIDEO LOGIC ---
  const toggleVideo = async () => {
    if (!videoEnabled) {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      videoRef.current.srcObject = stream;
      streamRef.current = stream;
      setVideoEnabled(true);
    } else {
      streamRef.current.getTracks().forEach(track => track.stop());
      setVideoEnabled(false);
    }
  };

  // --- VOICE LOGIC ---
  const startRecording = async () => {
    try {
      const stream = streamRef.current || await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      let chunks = [];

      mediaRecorderRef.current.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/wav" });
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = () => {
          const base64Audio = reader.result.split(",")[1];
          handleSendMessage(null, base64Audio, true);
        };
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) { alert("Microphone access denied"); }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleSendMessage = async (text, audioBase64 = null, speakResponse = false) => {
    const userDisplay = text || "🎤 Voice Input...";
    setChat(prev => [...prev, { sender: "user", text: userDisplay }]);
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text || "",
          audio: audioBase64,
          voice_enabled: speakResponse 
        }),
      });

      const data = await res.json();

      // Play Agent Voice
      if (speakResponse && data.audio_response) {
        const audio = new Audio(`data:audio/mp3;base64,${data.audio_response}`);
        audio.play();
      }

      setChat(prev => [...prev, { sender: "bot", text: data.response }]);
    } catch (e) { console.error(e); }
    setLoading(false);
    setMessage("");
  };

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h3>AI Agent Multimodal</h3>
        <button onClick={toggleVideo} style={videoBtnStyle}>
          {videoEnabled ? "Close Video" : "Open Video Chat"}
        </button>
      </div>

      <div style={{ display: "flex", gap: "20px" }}>
        {/* LEFT: Video Feed */}
        {videoEnabled && (
          <div style={videoContainer}>
            <video ref={videoRef} autoPlay muted style={videoStyle} />
            <div style={overlayLabel}>Live Agent Session</div>
          </div>
        )}

        {/* RIGHT: Chat UI */}
        <div style={chatBoxStyle}>
          <div style={messageArea}>
            {chat.map((m, i) => (
              <div key={i} style={{ textAlign: m.sender === "user" ? "right" : "left", margin: "10px 0" }}>
                <span style={{ 
                  background: m.sender === "user" ? "#007bff" : "#eee", 
                  color: m.sender === "user" ? "white" : "black",
                  padding: "8px 12px", borderRadius: "15px", display: "inline-block"
                }}>
                  {m.text}
                </span>
              </div>
            ))}
            {loading && <p style={{ color: "gray", fontSize: "12px" }}>Agent is thinking...</p>}
          </div>

          <div style={inputArea}>
            <input 
              value={message} 
              onChange={(e) => setMessage(e.target.value)} 
              placeholder="Type message..." 
              style={inputStyle} 
            />
            <button 
              onMouseDown={startRecording} 
              onMouseUp={stopRecording} 
              style={{ ...micStyle, background: isRecording ? "red" : "#28a745" }}
            >
              {isRecording ? "Listening..." : "🎤"}
            </button>
            <button onClick={() => handleSendMessage(message, null, false)} style={sendBtnStyle}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- STYLES ---
const containerStyle = { maxWidth: "1000px", margin: "20px auto", padding: "20px", background: "#f9f9f9", borderRadius: "12px" };
const headerStyle = { display: "flex", justifyContent: "space-between", marginBottom: "20px" };
const chatBoxStyle = { flex: 1, background: "white", borderRadius: "10px", padding: "15px", border: "1px solid #ddd" };
const messageArea = { height: "400px", overflowY: "auto", borderBottom: "1px solid #eee", marginBottom: "10px" };
const videoContainer = { width: "400px", position: "relative" };
const videoStyle = { width: "100%", borderRadius: "10px", background: "black", transform: "scaleX(-1)" };
const overlayLabel = { position: "absolute", top: 10, left: 10, color: "white", fontSize: "12px", background: "rgba(0,0,0,0.5)", padding: "2px 8px" };
const inputArea = { display: "flex", gap: "10px" };
const inputStyle = { flex: 1, padding: "10px", borderRadius: "5px", border: "1px solid #ccc" };
const micStyle = { border: "none", color: "white", padding: "10px", borderRadius: "5px", cursor: "pointer" };
const sendBtnStyle = { background: "#007bff", color: "white", border: "none", padding: "10px 20px", borderRadius: "5px", cursor: "pointer" };
const videoBtnStyle = { background: "#6c757d", color: "white", border: "none", padding: "5px 15px", borderRadius: "20px", cursor: "pointer" };

export default ChatPage;
























