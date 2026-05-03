import React, { useState } from "react";
import TrainSchedule from "./TrainSchedule";

function TrainSearch() {
  const [trainNo, setTrainNo] = useState("");
  const [submittedTrainNo, setSubmittedTrainNo] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (trainNo.trim() !== "") {
      setSubmittedTrainNo(trainNo.trim());
    }
  };

  return (
    <div>
      <h2>Train Search</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter train number..."
          value={trainNo}
          onChange={(e) => setTrainNo(e.target.value)}
          style={{ marginBottom: "10px", padding: "5px" }}
        />
        <button type="submit">Search</button>
      </form>

      {submittedTrainNo !== "" && <TrainSchedule trainNo={submittedTrainNo} />}
    </div>
  );
}

export default TrainSearch;
