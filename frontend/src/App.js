import React, { useEffect, useState } from 'react';
import { io } from "socket.io-client";

function App() {
  const [trains, setTrains] = useState([]);

  useEffect(() => {
    const socket = io("http://127.0.0.1:5000");

    socket.on("train_update", (data) => {
      setTrains(data); // data is an array of trains
    });

    return () => socket.disconnect();
  }, []);

  return (
    <div>
      <h1>AI Co-Pilot Dashboard</h1>
      {trains.length > 0 ? (
        <table border="1" style={{ marginTop: "20px", width: "60%" }}>
          <thead>
            <tr>
              <th>Train ID</th>
              <th>Speed (km/h)</th>
              <th>Position</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {trains.map(train => (
              <tr key={train.train_id}>
                <td>{train.train_id}</td>
                <td>{train.speed}</td>
                <td>{train.position.toFixed(2)}</td>
                <td>{train.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>Waiting for train updates...</p>
      )}
    </div>
  );
}

export default App;
