import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  Autocomplete,
} from "@mui/material";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Simple black marker icon
const markerIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// Sample US city+state options (you can expand this later or hook to an API)
const CITY_OPTIONS = [
  { city: "Chicago", state: "IL" },
  { city: "New York", state: "NY" },
  { city: "Los Angeles", state: "CA" },
  { city: "Houston", state: "TX" },
  { city: "Seattle", state: "WA" },
  { city: "Miami", state: "FL" },
  { city: "Denver", state: "CO" },
  { city: "Boston", state: "MA" },
];

function LocationMarker({ onSelect }) {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      onSelect({ lat, lng });
    },
  });
  return null;
}

export default function LocationStep({ location, setLocation, onNext }) {
  const [selectedCity, setSelectedCity] = useState(
    CITY_OPTIONS.find((opt) => opt.city === location.city) || null
  );

  const handleSelect = (coords) => {
    setLocation((prev) => ({
      ...prev,
      coordinates: coords,
    }));
  };

  const handleConfirm = () => {
    if (!selectedCity && !location.coordinates) {
      alert("Please choose a city or click on the map.");
      return;
    }

    setLocation((prev) => ({
      ...prev,
      city: selectedCity?.city || prev.city,
      region: selectedCity?.state || prev.region || "",
    }));

    onNext();
  };

  return (
    <Paper
      elevation={6}
      sx={{
        width: "100%",
        maxWidth: 980,
        p: 4,
        borderRadius: "20px",
        backgroundColor: "#FFFFFF",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        overflow: "hidden",
      }}
    >
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, textAlign: "center" }}>
        Choose your location!
      </Typography>

      {/* Autocomplete input for city/state */}
      <Autocomplete
        options={CITY_OPTIONS}
        value={selectedCity}
        onChange={(event, newValue) => setSelectedCity(newValue)}
        getOptionLabel={(option) => `${option.city}, ${option.state}`}
        renderInput={(params) => (
          <TextField
            {...params}
            label="City, State"
            variant="outlined"
            sx={{
              mb: 2,
              "& .MuiOutlinedInput-root": { borderRadius: "12px", backgroundColor: "#FAF9F6" },
            }}
          />
        )}
        sx={{ width: "100%", mb: 2 }}
      />

      {/* Map */}
      <Box
        sx={{
          width: "100%",
          height: 400,
          borderRadius: "12px",
          overflow: "hidden",
          mb: 2,
        }}
      >
        <MapContainer
          center={[41.8781, -87.6298]} // default Chicago
          zoom={10}
          style={{ width: "100%", height: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {location.coordinates && (
            <Marker
              position={[location.coordinates.lat, location.coordinates.lng]}
              icon={markerIcon}
            />
          )}
          <LocationMarker onSelect={handleSelect} />
        </MapContainer>
      </Box>

      {/* Summary display */}
      {(selectedCity || location.coordinates) && (
        <Box sx={{ textAlign: "center", mb: 2 }}>
          <Typography variant="body1" sx={{ color: "#333", fontWeight: 600 }}>
            {selectedCity
              ? `${selectedCity.city}, ${selectedCity.state}`
              : location.city
              ? `${location.city}, ${location.region || ""}`
              : "—"}
          </Typography>
          {location.coordinates && (
            <Typography variant="body2" sx={{ color: "#555" }}>
              {location.coordinates.lat.toFixed(4)}° N,{" "}
              {location.coordinates.lng.toFixed(4)}° W
            </Typography>
          )}
        </Box>
      )}

      {/* Buttons */}
      <Box sx={{ display: "flex", justifyContent: "flex-end", width: "100%", mt: 1 }}>
        <Button
          variant="contained"
          onClick={handleConfirm}
          sx={{
            backgroundColor: "#F6D76F",
            color: "#000",
            borderRadius: "12px",
            textTransform: "none",
            fontWeight: 600,
            px: 4,
            py: 1,
            "&:hover": { backgroundColor: "#F3CD52" },
          }}
        >
          Next
        </Button>
      </Box>
    </Paper>
  );
}
