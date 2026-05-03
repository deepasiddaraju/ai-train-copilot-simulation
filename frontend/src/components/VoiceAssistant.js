import React, { useState } from "react";
import axios from "axios";

function VoiceAssistant() {
  const [response, setResponse] = useState(null);
  const [listening, setListening] = useState(false);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition not supported in this browser. Use Google Chrome.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    recognition.onresult = async (event) => {
      const query = event.results[0][0].transcript;
      try {
        const res = await axios.post("http://127.0.0.1:5000/voice_query", { query });
        setResponse(res.data);

        // Speak back the response
        const utterance = new SpeechSynthesisUtterance(res.data.message);
        window.speechSynthesis.speak(utterance);
      } catch {
        setResponse({ message: "Error contacting AI Copilot backend." });
      }
    };

    recognition.start();
  };

  const renderTable = () => {
    if (!response || !response.details || !Array.isArray(response.details)) return null;

    if (response.type === "delay") {
      // Prediction results (ML model)
      return (
        <table border="1" cellPadding="8" style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Station Code</th>
              <th>Station Name</th>
              <th>Predicted Delay (min)</th>
            </tr>
          </thead>
          <tbody>
            {response.details.map((row, idx) => (
              <tr key={idx}>
                <td>{row.station_code}</td>
                <td>{row.station_name}</td>
                <td>{row.predicted_delay_minutes ?? "N/A"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      );
    } else if (response.type === "skip" || response.type === "reroute") {
      // What-If results (scenario simulation)
      return (
        <table border="1" cellPadding="8" style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>Station Code</th>
              <th>Predicted Delay (min)</th>
              <th>Likely Cause</th>
            </tr>
          </thead>
          <tbody>
            {response.details.map((row, idx) => (
              <tr key={idx}>
                <td>{row.station_code}</td>
                <td>{row.predicted_delay ?? "N/A"}</td>
                <td>
                  {row.likely_cause === "Skipped station"
                    ? "Skipped station"
                    : row.likely_cause ?? "N/A"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      );
    }

    return null;
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Voice Assistant</h2>
      <button onClick={startListening}>🎤 Ask AI Copilot</button>
      {listening && <p style={{ color: "blue" }}>Listening...</p>}

      {response && (
        <div style={{ marginTop: "20px" }}>
          <h3>{response.message}</h3>
          {renderTable()}
        </div>
      )}
    </div>
  );
}

export default VoiceAssistant;
