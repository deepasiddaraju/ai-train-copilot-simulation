import React, { useEffect, useState } from 'react';

function App() {
  const [train, setTrain] = useState(null);

  

  useEffect(() => {
  const interval = setInterval(() => {
    fetch("http://127.0.0.1:5000/api/train_status")
      .then(res => res.json())
      .then(data => setTrain(data));
  }, 2000); // refresh every 2 seconds
  return () => clearInterval(interval);
}, []);


  return (
    <div>
      <h1>AI Co-Pilot Dashboard</h1>
      {train ? (
        <p>Train {train.train_id} → Speed: {train.speed} km/h, Position: {train.position}</p>
      ) : (
        <p>Loading train data...</p>
      )}
    </div>
  );
}

export default App;
