import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Button,
  TextField,
  Autocomplete,
  Fade,
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
  { city: "Chicago", state: "IL", lat: 41.8781, lng: -87.6298 },
  { city: "New York", state: "NY", lat: 40.7128, lng: -74.006 },
  { city: "Los Angeles", state: "CA", lat: 34.0522, lng: -118.2437 },
  { city: "Houston", state: "TX", lat: 29.7604, lng: -95.3698 },
  { city: "Seattle", state: "WA", lat: 47.6062, lng: -122.3321 },
  { city: "Miami", state: "FL", lat: 25.7617, lng: -80.1918 },
  { city: "Denver", state: "CO", lat: 39.7392, lng: -104.9903 },
  { city: "Boston", state: "MA", lat: 42.3601, lng: -71.0589 },
];

// Detect map clicks or drags
function LocationMarker({ onSelect }) {
  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      onSelect({ lat, lng });
    },
    dragend(e) {
      const center = e.target.getCenter();
      onSelect({ lat: center.lat, lng: center.lng });
    },
  });
  return null;
}

export default function LocationStep({ location, setLocation, onNext }) {
  const [selectedCity, setSelectedCity] = useState(
    CITY_OPTIONS.find((opt) => opt.city === location.city) || null
  );
  const [showSummary, setShowSummary] = useState(false);

  const handleSelect = (coords) => {
    setLocation((prev) => ({
      ...prev,
      coordinates: coords,
    }));
    setShowSummary(true);
  };

  const handleCitySelect = (newValue) => {
    setSelectedCity(newValue);
    if (newValue) {
      setLocation((prev) => ({
        ...prev,
        city: newValue.city,
        region: newValue.state,
        coordinates: { lat: newValue.lat, lng: newValue.lng },
      }));
    }
    setShowSummary(!!newValue);
  };

  const handleConfirm = () => {
    if (!selectedCity && !location.coordinates) {
      alert("Please choose a city or click on the map.");
      return;
    }

    // Preserve existing info
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
        onChange={(event, newValue) => handleCitySelect(newValue)}
        getOptionLabel={(option) => `${option.city}, ${option.state}`}
        renderInput={(params) => (
          <TextField
            {...params}
            label="City, State"
            variant="outlined"
            sx={{
              mb: 2,
              "& .MuiOutlinedInput-root": {
                borderRadius: "12px",
                backgroundColor: "#FAF9F6",
              },
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
          center={location.coordinates || [41.8781, -87.6298]} // default Chicago
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
              draggable={true}
              eventHandlers={{
                dragend: (e) => {
                  const newPos = e.target.getLatLng();
                  handleSelect(newPos);
                },
              }}
            />
          )}
          <LocationMarker onSelect={handleSelect} />
        </MapContainer>
      </Box>

      {/* Smooth fade-in green summary box */}
      <Fade in={showSummary} timeout={600}>
        <Box
          sx={{
            mt: 2,
            mb: 2,
            px: 3,
            py: 1.5,
            backgroundColor: "#C8EAC5",
            borderRadius: "12px",
            textAlign: "center",
            width: "fit-content",
            mx: "auto",
            boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
          }}
        >
          <Typography
            variant="body1"
            sx={{
              color: "#143E1B",
              fontWeight: 700,
            }}
          >
            {selectedCity
              ? `${selectedCity.city}, ${selectedCity.state}`
              : location.city
              ? `${location.city}${location.region ? `, ${location.region}` : ""}`
              : "—"}
          </Typography>

          {location.coordinates && (
            <Typography
              variant="body2"
              sx={{
                color: "#143E1B",
                fontWeight: 600,
                letterSpacing: "0.01em",
              }}
            >
              {location.coordinates.lat.toFixed(4)}° N,{" "}
              {location.coordinates.lng.toFixed(4)}° W
            </Typography>
          )}
        </Box>
      </Fade>

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
