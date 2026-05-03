import React, { useState } from "react";
import axios from "axios";

function TrainSchedule() {
  const [trainNo, setTrainNo] = useState("");
  const [schedule, setSchedule] = useState([]);
  const [error, setError] = useState("");

  const handleSearch = () => {
    setError("");
    setSchedule([]);

    axios.get(`http://127.0.0.1:5000/train/${trainNo}`)
      .then(res => {
        const data = res.data;
        if (Array.isArray(data)) {
          setSchedule(data);
        } else {
          // If backend returns {}, null, or string
          setSchedule([]);
          setError("No schedule found for this train number.");
        }
      })
      .catch(() => {
        setSchedule([]);
        setError("Error fetching schedule.");
      });
  };

  return (
    <div>
      <h2>Train Schedule</h2>
      <input
        value={trainNo}
        onChange={e => setTrainNo(e.target.value)}
        placeholder="Enter train number"
      />
      <button onClick={handleSearch}>Get Schedule</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {schedule.length > 0 ? (
        <table border="1" style={{ marginTop: "10px", width: "100%" }}>
          <thead>
            <tr>
              <th>Day</th>
              <th>Station</th>
              <th>Arrival</th>
              <th>Departure</th>
              <th>Zone</th>
            </tr>
          </thead>
          <tbody>
            {schedule.map((s, i) => (
              <tr key={i}>
                <td>{s.day}</td>
                <td>{s.station_name}</td>
                <td>{s.arrival}</td>
                <td>{s.departure}</td>
                <td>{s.zone}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        !error && <p>No schedule to display.</p>
      )}
    </div>
  );
}

export default TrainSchedule;
