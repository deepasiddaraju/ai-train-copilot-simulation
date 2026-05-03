import React from "react";
import "./dashboard.css";   // ✅ global styles
import Dashboard from "./components/Dashboard";

function App() {
  return (
    <div className="app-container">
      <h1 className="app-header">🚆 Indian Railways  Dashboard</h1>
      <Dashboard />
    </div>
  );
}

export default App;
