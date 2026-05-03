import React, { useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer
} from "recharts";



function PredictionsTab() {
  const [trainNo, setTrainNo] = useState("");
  const [skipStation, setSkipStation] = useState("");
  const [reroute, setReroute] = useState("");
  const [scenario, setScenario] = useState({});
  const [whatIfResults, setWhatIfResults] = useState([]);
  const [baselineResults, setBaselineResults] = useState([]);
  const [comparisonSummary, setComparisonSummary] = useState(null);
  const [driverMessages, setDriverMessages] = useState([]);
  const [alerts, setAlerts] = useState([]);
  


  // Generate proactive alerts after simulation
const generateAlerts = (baselineResults, whatIfResults, scenario, comparisonSummary) => {
  const alerts = [];

  // Threshold check: any station delay > 30 min
  whatIfResults.forEach(r => {
    if (r.predicted_delay >= 30) {
      alerts.push(`⚠️ High delay at ${r.station_code}: ${r.predicted_delay} min. Cause: ${r.likely_cause}.`);
    }

    // Risk-based alert
    const risk = getRiskScore(r.predicted_delay);
    if (risk.level === "High") {
      alerts.push(`🔴 High Risk Alert: ${r.station_code} predicted delay ${r.predicted_delay} min. Immediate attention required.`);
    }
  });

  // Reroute recommendation
  if (scenario.reroute && scenario.reroute.length > 0 && comparisonSummary.whatIfTotal < comparisonSummary.baselineTotal) {
    alerts.push(`✅ Recommended Action: Reroute via ${scenario.reroute.join(" → ")} to save ${comparisonSummary.baselineTotal - comparisonSummary.whatIfTotal} minutes.`);
  }

  return alerts;
};

const dismissAlert = (index) => {
  setAlerts(prev => prev.filter((_, i) => i !== index));
};

// Risk score helper
const getRiskScore = (delay) => {
  if (delay <= 5) return { level: "Low", color: "green" };
  if (delay <= 20) return { level: "Medium", color: "orange" };
  return { level: "High", color: "red" };
};


  const runSimulation = async () => {
    if (!trainNo.trim()) {
      alert("Please select a train number before running simulation.");
      return;
    }

    // ✅ Clear old driver messages
  setDriverMessages([]);

    // Baseline run
    const baselineRes = await axios.post("http://127.0.0.1:5000/analytics/what_if", {
      train_no: trainNo,
      scenario: {}
    });
    setBaselineResults(baselineRes.data.results);

    // What-if run with scenario overrides
    const res = await axios.post("http://127.0.0.1:5000/analytics/what_if", {
      train_no: trainNo,
      scenario: {
        ...scenario,
        skip_station: skipStation.trim() || undefined,
        reroute: reroute ? reroute.split(",").map(s => s.trim()).filter(s => s) : undefined
      }
    });
    setWhatIfResults(res.data.results);

    const baselineTotal = baselineRes.data.results.reduce((sum, r) => sum + (r.predicted_delay || 0), 0);
    const whatIfTotal = res.data.results.reduce((sum, r) => sum + (r.predicted_delay || 0), 0);
    setComparisonSummary({ baselineTotal, whatIfTotal });

     const newAlerts = generateAlerts(
  baselineRes.data.results,
  res.data.results,
  {
    ...scenario,
    reroute: reroute ? reroute.split(",").map(s => s.trim()).filter(s => s) : undefined
  },
  { baselineTotal, whatIfTotal }
);

setAlerts(newAlerts);

newAlerts.forEach(alert => {
  const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  setDriverMessages(prev => [...prev, `${timestamp} – ${alert}`]);
});


  };
  



  // ✅ Match by station_code instead of index
  const chartData = baselineResults.map(base => {
    const match = whatIfResults.find(r => r.station_code === base.station_code);
    return {
      station_code: base.station_code,
      baseline_delay: base.predicted_delay,
      whatif_delay: match ? match.predicted_delay : 0
    };
  });

  
 

  const sendToDriver = () => {
  if (comparisonSummary) {
    let message = "";
    if (comparisonSummary.whatIfTotal < comparisonSummary.baselineTotal) {
      if (skipStation) {
        message = `Train ${trainNo}: Improved delays by ${comparisonSummary.baselineTotal - comparisonSummary.whatIfTotal} min by skipping ${skipStation}. Cause: ${whatIfResults[0]?.likely_cause || "N/A"} (Weather: ${whatIfResults[0]?.weather_condition || "N/A"}).`;
      } else if (scenario.reroute && scenario.reroute.length > 0) {
        message = `Train ${trainNo}: Improved delays by ${comparisonSummary.baselineTotal - comparisonSummary.whatIfTotal} min by rerouting via ${scenario.reroute.join(" → ")}. Cause: ${whatIfResults[0]?.likely_cause || "N/A"} (Weather: ${whatIfResults[0]?.weather_condition || "N/A"}).`;
      } else {
        message = `Train ${trainNo}: Improved delays by ${comparisonSummary.baselineTotal - comparisonSummary.whatIfTotal} min. Cause: ${whatIfResults[0]?.likely_cause || "N/A"} (Weather: ${whatIfResults[0]?.weather_condition || "N/A"}).`;
      }
    } else if (comparisonSummary.whatIfTotal > comparisonSummary.baselineTotal) {
      message = `Train ${trainNo}: Worsened delays by ${comparisonSummary.whatIfTotal - comparisonSummary.baselineTotal} min. Cause: ${whatIfResults[0]?.likely_cause}.`;
    } else {
      message = `Train ${trainNo}: No change in delays.`;
    }

    // ✅ Add timestamp
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const messageWithTime = `${timestamp} – ${message}`;

    setDriverMessages([...driverMessages, messageWithTime]);
  } else {
    alert("Run a simulation first to generate a driver message.");
  }
};

  return (
    <div>
      <h2>AI Delay Predictions</h2>

      <div className="chart-box">
        <h3>What‑If Simulation</h3>

        <label>Select Train Number: </label>
        <select value={trainNo} onChange={(e) => setTrainNo(e.target.value)}>
          <option value="">-- Select --</option>
          <option value="12673">12673</option>
          <option value="12674">12674</option>
          <option value="12681">12681</option>
          <option value="12682">12682</option>
          <option value="12433">12433</option>
          <option value="12434">12434</option>
          <option value="12839">12839</option>
          <option value="12840">12840</option>
        </select>

        <input
          type="text"
          value={skipStation}
          onChange={(e) => setSkipStation(e.target.value)}
          placeholder="Skip station code (optional)"
        />
        <input
          type="text"
          value={reroute}
          onChange={(e) => setReroute(e.target.value)}
          placeholder="Reroute stations comma-separated (optional)"
        />

        {/* Weather & Maintenance Toggles */}
        <div style={{ marginTop: "10px" }}>
          <label>
            <input
              type="checkbox"
              checked={scenario.weather === "rain"}
              onChange={(e) => setScenario(prev => ({ ...prev, weather: e.target.checked ? "rain" : "" }))}
            />
            Simulate Rain
          </label>
          <label style={{ marginLeft: "15px" }}>
            <input
              type="checkbox"
              checked={scenario.weather === "fog"}
              onChange={(e) => setScenario(prev => ({ ...prev, weather: e.target.checked ? "fog" : "" }))}
            />
            Simulate Fog
          </label>
          <label style={{ marginLeft: "15px" }}>
            <input
              type="checkbox"
              checked={scenario.maintenance || false}
              onChange={(e) => setScenario(prev => ({ ...prev, maintenance: e.target.checked }))}
            />
            Maintenance Impact
          </label>
        </div>

        <button onClick={runSimulation}>Run Simulation</button>

        {Array.isArray(whatIfResults) && whatIfResults.length > 0 ? (
          <div className="results-box">
            <h4>Simulation Results</h4>
            
   {alerts.length > 0 && (
  <div className="alerts-panel" style={{ marginBottom: "15px" }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <h4 style={{ margin: 0 }}>Proactive Alerts</h4>
      <button
        onClick={() => setAlerts([])}
        style={{
          padding: "6px 10px",
          backgroundColor: "#FF4C4C",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer"
        }}
      >
        Clear All Alerts
      </button>
    </div>

    {alerts.map((alert, idx) => (
      <div
        key={idx}
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "10px",
          marginTop: "8px",
          borderRadius: "6px",
          fontWeight: "bold",
          color: alert.includes("⚠️") ? "white" : "green",
          backgroundColor: alert.includes("⚠️") ? "red" : "#e6ffe6",
          border: alert.includes("⚠️") ? "2px solid darkred" : "2px solid green"
        }}
      >
        <span>{alert}</span>
        <button
          onClick={() => dismissAlert(idx)}
          style={{
            marginLeft: "10px",
            padding: "4px 8px",
            backgroundColor: "#444",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          ✖
        </button>
      </div>
    ))}
  </div>
)}

            <ul>
              {whatIfResults.map((r, idx) => {
                const isRerouted = scenario.reroute && scenario.reroute.includes(r.station_code);
                return (
                  <li
  key={idx}
  style={{
    fontWeight: "bold",
    border: isRerouted ? "2px solid green" : "none",
    padding: "6px",
    marginBottom: "6px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#f9f9f9",
    borderRadius: "6px"
  }}
>
  <span>
    {r.station_code}: {r.predicted_delay} min ({r.likely_cause} | Weather: {r.weather_condition})
  </span>
  {(() => {
    const risk = getRiskScore(r.predicted_delay);
    return (
      <span
        style={{
          marginLeft: "12px",
          fontWeight: "bold",
          color: risk.color
        }}
      >
        Risk: {risk.level}
      </span>
    );
  })()}
</li>

                );
              })}
            </ul>

            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <XAxis dataKey="station_code" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="baseline_delay" stroke="#FF8042" name="Original Route" />
                <Line type="monotone" dataKey="whatif_delay" stroke="#0088FE" name="What-If Route" />
              </LineChart>
            </ResponsiveContainer>
{comparisonSummary && (
  <div className="summary-box">
    <p>
      Total Delay (Original): {comparisonSummary.baselineTotal} min | 
      Total Delay (What-If): {comparisonSummary.whatIfTotal} min
    </p>
    {comparisonSummary.whatIfTotal === comparisonSummary.baselineTotal ? (
      <p style={{ fontWeight: "bold", color: "gray" }}>No Change</p>
    ) : comparisonSummary.whatIfTotal < comparisonSummary.baselineTotal ? (
      <div>
        <p style={{ fontWeight: "bold", color: "green" }}>
          {scenario.reroute && scenario.reroute.length > 0
            ? `Reroute improved delays by ${comparisonSummary.baselineTotal - comparisonSummary.whatIfTotal} min`
            : `Improvement: Reduced by ${comparisonSummary.baselineTotal - comparisonSummary.whatIfTotal} min`}
        </p>
        {scenario.reroute && scenario.reroute.length > 0 && (
          <div style={{
            marginTop: "10px",
            padding: "10px",
            backgroundColor: "#e6ffe6",
            border: "2px solid green",
            borderRadius: "6px",
            fontWeight: "bold"
          }}>
            ✅ Recommended Action: Reroute via {scenario.reroute.join(" → ")}  
            to save {comparisonSummary.baselineTotal - comparisonSummary.whatIfTotal} minutes.
          </div>
        )}
        
      </div>
    ) : (
      <p style={{ fontWeight: "bold", color: "red" }}>
        {scenario.reroute && scenario.reroute.length > 0
          ? `Reroute worsened delays by ${comparisonSummary.whatIfTotal - comparisonSummary.baselineTotal} min`
          : `Worsened: Increased by ${comparisonSummary.whatIfTotal - comparisonSummary.baselineTotal} min`}
      </p>
    )}
    
  </div>
)}


            

            <button onClick={sendToDriver}
              style={{ marginTop: "10px", padding: "8px 12px", backgroundColor: "#0088FE", color: "white", border: "none", borderRadius: "4px" }}>
              Send to Driver
            </button>

                       {driverMessages.length > 0 && (
              <div className="driver-messages" style={{ marginTop: "15px" }}>
                <h4>Driver Messages</h4>
                <ul>
                  {driverMessages.map((msg, idx) => (
                    <li key={idx} style={{ fontStyle: "italic" }}>{msg}</li>
                  ))}
                </ul>
                {/* ✅ Clear button */}
    <button
      onClick={() => setDriverMessages([])}
      style={{
        marginTop: "10px",
        padding: "6px 10px",
        backgroundColor: "#FF4C4C",
        color: "white",
        border: "none",
        borderRadius: "4px",
        cursor: "pointer"
      }}
    >
      Clear Messages
    </button>
              </div>
            )}
          </div>
        ) : (
          <p>No results found for this train/scenario.</p>
        )}
      </div>
    </div>
  );
}

export default PredictionsTab;
