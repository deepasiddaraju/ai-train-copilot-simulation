import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet/dist/images/marker-shadow.png",
});

// Helper component to recenter map when stations change
function RecenterMap({ stations }) {
  const map = useMap();
  useEffect(() => {
    if (Array.isArray(stations) && stations.length > 0) {
      const firstValid = stations.find(
        (s) => s.lat !== undefined && s.lon !== undefined
      );
      if (firstValid) {
        map.setView([parseFloat(firstValid.lat), parseFloat(firstValid.lon)], 8);
      }
    }
  }, [stations, map]);
  return null;
}

function StationMap({ stations }) {
  return (
    <MapContainer
      center={[28.642314, 77.220004]} // default center (New Delhi)
      zoom={6}
      style={{ height: "400px", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {Array.isArray(stations) &&
        stations
          .filter((s) => s.lat !== undefined && s.lon !== undefined)
          .map((s, i) => (
            <Marker
              key={i}
              position={[parseFloat(s.lat), parseFloat(s.lon)]}
            >
              <Popup>
                <strong>{s.station_name}</strong><br />
                Code: {s.station_code}<br />
                Zone: {s.zone}
              </Popup>
            </Marker>
          ))}
      <RecenterMap stations={stations} />
    </MapContainer>
  );
}

export default StationMap;
