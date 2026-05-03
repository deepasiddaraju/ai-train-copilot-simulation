import React, { useState, useEffect } from "react";
import axios from "axios";
import StationMap from "./StationMap";

function StationSearch() {
  const [query, setQuery] = useState("");
  const [stations, setStations] = useState([]);

  useEffect(() => {
    if (query.trim() === "") {
      // ✅ Clear results when input is empty
      setStations([]);
      return;
    }

    axios
      .get(`http://127.0.0.1:5000/stations/search?name=${query}`)
      .then((res) => {
        const data = Array.isArray(res.data) ? res.data : [res.data];
        setStations(data);
      })
      .catch(() => setStations([]));
  }, [query]);

  return (
    <div>
      <h2>Station Search</h2>
      <input
        type="text"
        placeholder="Enter station name..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{ marginBottom: "10px", padding: "5px" }}
      />

      {/* Table */}
      {stations.length > 0 && (
        <table border="1" style={{ marginBottom: "20px", width: "100%" }}>
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Zone</th>
              <th>Lat</th>
              <th>Lon</th>
            </tr>
          </thead>
          <tbody>
            {stations.map((s, i) => (
              <tr key={i}>
                <td>{s.station_code}</td>
                <td>{s.station_name}</td>
                <td>{s.zone}</td>
                <td>{s.lat}</td>
                <td>{s.lon}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Map */}
      <StationMap stations={stations} />
    </div>
  );
}

export default StationSearch;
