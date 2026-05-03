import React, { useState, useEffect } from "react";
import axios from "axios";
import TrainPrediction from "./TrainPrediction";
import StationMap from "./StationMap";
import TrainSchedule from "./TrainSchedule";
import PredictionsTab from "./PredictionsTab";
import VoiceAssistant from "./VoiceAssistant";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";
import "../dashboard.css";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A28EFF", "#FF6F61"];

function Dashboard() {
  const [activeTab, setActiveTab] = useState("analytics");
  const [busiest, setBusiest] = useState([]);
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    if (activeTab === "analytics") {
      axios.get("http://127.0.0.1:5000/analytics/busiest").then(res => setBusiest(res.data));
      axios.get("http://127.0.0.1:5000/analytics/zone").then(res => setZones(res.data));
    }
  }, [activeTab]);

  const handleSearch = async () => {
    try {
      const res = await axios.get(`http://127.0.0.1:5000/stations/search?name=${searchQuery}`);
      const data = Array.isArray(res.data) ? res.data : [res.data];
      setSearchResults(data);
    } catch {
      setSearchResults([{ message: "Error fetching search results" }]);
    }
  };

  const filteredStations =
    selectedZone === "ALL"
      ? busiest
      : busiest.filter(station => station.zone === selectedZone);

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2 className="sidebar-title">Navigation</h2>
        <ul className="sidebar-list">
          <li
            className={activeTab === "analytics" ? "active" : ""}
            onClick={() => setActiveTab("analytics")}
          >
            Analytics
          </li>
          <li
            className={activeTab === "predictions" ? "active" : ""}
            onClick={() => setActiveTab("predictions")}
          >
            Predictions
          </li>
          <li
            className={activeTab === "search" ? "active" : ""}
            onClick={() => setActiveTab("search")}
          >
            Search
          </li>
          <li
            className={activeTab === "schedule" ? "active" : ""}
            onClick={() => setActiveTab("schedule")}
          >
            Train Schedule
          </li>

          <li
  className={activeTab === "voice" ? "active" : ""}
  onClick={() => setActiveTab("voice")}
>
  Voice Assistant
</li>

        </ul>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {activeTab === "analytics" && (
          <div>
            <h2>Analytics Dashboard</h2>

            {/* Filter Dropdown */}
            <label>Filter by Zone: </label>
            <select
              value={selectedZone}
              onChange={(e) => setSelectedZone(e.target.value)}
            >
              <option value="ALL">All Zones</option>
              {zones.map((z, idx) => (
                <option key={idx} value={z.zone}>
                  {z.zone}
                </option>
              ))}
            </select>

            <div className="charts-container">
              {/* Busiest Stations Bar Chart */}
              <div className="chart-box">
                <h3>Busiest Stations</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={filteredStations}>
                    <XAxis dataKey="station_name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="traffic" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Zone Density Pie Chart */}
              <div className="chart-box">
                <h3>Zone Density</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={zones}
                      dataKey="station_count"
                      nameKey="zone"
                      cx="50%"
                      cy="50%"
                      outerRadius={120}
                      label
                    >
                      {zones.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === "predictions" && (
          <div>
            <TrainPrediction />
            <PredictionsTab />
          </div>
        )}

        {activeTab === "search" && (
          <div>
            <h2>Search Stations</h2>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter station name or code"
              className="primary-input"
            />
            <button className="primary-button" onClick={handleSearch}>
              Search
            </button>

            {searchResults.length > 0 && (
              <>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Station Code</th>
                      <th>Station Name</th>
                      <th>Zone</th>
                      <th>Latitude</th>
                      <th>Longitude</th>
                    </tr>
                  </thead>
                  <tbody>
                    {searchResults.map((row, idx) => (
                      <tr key={idx}>
                        <td>{row.station_code}</td>
                        <td>{row.station_name}</td>
                        <td>{row.zone}</td>
                        <td>{row.lat}</td>
                        <td>{row.lon}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {/* Map */}
                <StationMap stations={searchResults} />
              </>
            )}
          </div>
        )}

        {activeTab === "schedule" && <TrainSchedule />}

        {activeTab === "voice" && <VoiceAssistant />}
      </div>

      

    </div>
  );
}

export default Dashboard;
