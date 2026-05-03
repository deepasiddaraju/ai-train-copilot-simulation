import React, { useEffect, useState } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function BusiestStations() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/analytics/busiest")
      .then(res => setData(res.data));
  }, []);

  return (
    <div>
      <h2>Busiest Stations</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <XAxis dataKey="station_name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="traffic" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BusiestStations;
