import React, { useState } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

function TrainPrediction() {
  const [trainNo, setTrainNo] = useState("");
  const [prediction, setPrediction] = useState(null);

  const handlePredict = async () => {
    try {
      const res = await axios.get(`http://127.0.0.1:5000/predict/${trainNo}`);
      setPrediction(res.data);
    } catch (err) {
      setPrediction({ message: "Error fetching prediction" });
    }
  };

  const isArray = Array.isArray(prediction);

  // Helper function to pick color
  const getColor = (delay) => {
    if (delay === null || delay === undefined) return "gray";
    if (delay === 0) return "green";
    if (delay > 0 && delay <= 5) return "orange";
    if (delay >= 10) return "red";
    return "gray";
  };

  // Custom Leaflet icon generator
  const createIcon = (color) =>
    L.divIcon({
      className: "custom-icon",
      html: `<div style="background-color:${color}; width:16px; height:16px; border-radius:50%; border:2px solid white;"></div>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8],
    });

  // Summary calculation
  const getSummary = () => {
    if (!isArray) return null;
    let onTime = 0, slight = 0, significant = 0, na = 0;
    prediction.forEach((row) => {
      const d = row.predicted_delay_minutes;
      if (d === null || d === undefined) na++;
      else if (d === 0) onTime++;
      else if (d > 0 && d <= 5) slight++;
      else if (d >= 10) significant++;
    });
    return { onTime, slight, significant, na };
  };

  const summary = getSummary();

  return (
    <div style={{ padding: "20px" }}>
      <h2>AI Delay Prediction (Forecast)</h2>
      <input
        type="text"
        value={trainNo}
        onChange={(e) => setTrainNo(e.target.value)}
        placeholder="Enter train number"
        style={{ marginRight: "10px" }}
      />
      <button onClick={handlePredict}>Predict</button>

      {isArray && prediction.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3>
            Forecast for Train {prediction[0].train_no} ({prediction[0].train_name})
          </h3>

          {/* Legend */}
          <div style={{ marginBottom: "10px" }}>
            <strong>Legend:</strong>
            <div style={{ display: "flex", gap: "20px", marginTop: "5px" }}>
              <span style={{ backgroundColor: "green", color: "white", padding: "4px 8px" }}>
                On Time (0 min)
              </span>
              <span style={{ backgroundColor: "orange", color: "white", padding: "4px 8px" }}>
                Slight Delay (1–5 min)
              </span>
              <span style={{ backgroundColor: "red", color: "white", padding: "4px 8px" }}>
                Significant Delay (≥10 min)
              </span>
              <span style={{ backgroundColor: "gray", color: "white", padding: "4px 8px" }}>
                N/A (No prediction)
              </span>
            </div>
          </div>

          {/* Alert banner */}
          {summary && summary.significant > 0 && (
            <div style={{ 
              backgroundColor: "red", 
              color: "white", 
              padding: "10px", 
              marginBottom: "10px", 
              fontWeight: "bold" 
            }}>
              ⚠️ Alert: {summary.significant} stations predicted with significant delays!
            </div>
          )}

          {/* Map View */}
          <MapContainer center={[23.2, 80.0]} zoom={6} style={{ height: "400px", width: "100%", marginBottom: "20px" }}>
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap contributors"
            />
            {prediction.map((row, idx) =>
              row.lat && row.lon ? (
                <Marker
                  key={idx}
                  position={[row.lat, row.lon]}
                  icon={createIcon(getColor(row.predicted_delay_minutes))}
                >
                  <Popup>
                    <strong>{row.station_name}</strong><br />
                    Delay: {row.predicted_delay_minutes ?? "N/A"} min
                  </Popup>
                </Marker>
              ) : null
            )}
          </MapContainer>

          {/* Table View */}
          <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                <th>Station Code</th>
                <th>Station Name</th>
                <th>Predicted Delay (min)</th>
              </tr>
            </thead>
            <tbody>
              {prediction.map((row, idx) => (
                <tr key={idx}>
                  <td>{row.station_code}</td>
                  <td>{row.station_name}</td>
                  <td
                    style={{
                      color: "white",
                      backgroundColor: getColor(row.predicted_delay_minutes),
                      textAlign: "center",
                      fontWeight: "bold"
                    }}
                  >
                    {row.predicted_delay_minutes ?? "N/A"}
                  </td>
                </tr>
              ))}
              {/* Summary row */}
              {summary && (
                <tr style={{ fontWeight: "bold", backgroundColor: "#f0f0f0" }}>
                  <td colSpan="2">Summary</td>
                  <td>
                    On Time: {summary.onTime} | Slight: {summary.slight} | Significant: {summary.significant} | N/A: {summary.na}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {!isArray && prediction && prediction.message && (
        <p style={{ marginTop: "20px" }}>{prediction.message}</p>
      )}
    </div>
  );
}

export default TrainPrediction;
