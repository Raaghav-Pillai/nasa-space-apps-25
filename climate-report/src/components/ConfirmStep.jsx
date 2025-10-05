import React, { useState } from "react";
import { Box, Typography, Paper, Button, Divider, CircularProgress } from "@mui/material";

export default function ConfirmStep({ location, profile, dates, onBack }) {
  // Colors
  const gold = "#F6D76F";
  const lightBg = "#FAF9F6";
  const darkText = "#615b40";

  // Loading + feedback state
  const [loading, setLoading] = useState(false);

  // --- Extract data safely ---
  const t = profile?.traits || {};
  const temp = t.tempRange || t.temperature || ["—", "—"];
  const wind = t.windMaxMph || t.wind || "—";

  // --- Format location ---
  const hasCity = location?.city;
  const hasCoords = location?.coordinates?.lat && location?.coordinates?.lng;

  const locationText = hasCity
    ? `${location.city}${location.region ? `, ${location.region}` : ""}${
        location.country ? `, ${location.country}` : ""
      }${hasCoords ? `\n${location.coordinates.lat.toFixed(4)}° N, ${location.coordinates.lng.toFixed(4)}° W` : ""}`
    : hasCoords
    ? `${location.coordinates.lat.toFixed(4)}° N, ${location.coordinates.lng.toFixed(4)}° W`
    : "—";

  // --- Format date range ---
  const start = dates?.startDate
    ? `${dates.startDate} ${dates.startTime || "00:00:00"}`
    : "—";
  const end = dates?.endDate
    ? `${dates.endDate} ${dates.endTime || "23:59:59"}`
    : "—";

  // --- Submit function ---
  const handleSubmit = async () => {
    const payload = { location, profile, dates };
    console.log("📦 Sending payload:", payload);

    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      console.log("✅ Response from backend:", data);
      alert("✅ Report successfully sent! Check console for backend response.");
    } catch (err) {
      console.error("❌ Failed to send data:", err);
      alert("❌ Failed to send data to backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      elevation={4}
      sx={{
        width: "100%",
        maxWidth: 980,
        p: 4,
        borderRadius: "20px",
        backgroundColor: "#fff",
        display: "flex",
        flexDirection: "column",
        alignItems: "stretch",
      }}
    >
      <Typography variant="h6" fontWeight={700} color={darkText} sx={{ mb: 2 }}>
        Confirm your selection!
      </Typography>

      {/* --- LOCATION --- */}
      <Box
        sx={{
          backgroundColor: lightBg,
          borderRadius: "12px",
          p: 2,
          mb: 2,
        }}
      >
        <Typography fontWeight={700} color={darkText}>
          Location
        </Typography>
        <Typography sx={{ whiteSpace: "pre-line", color: darkText }}>
          {locationText}
        </Typography>
      </Box>

      {/* --- PROFILE --- */}
      <Box
        sx={{
          backgroundColor: gold,
          borderRadius: "12px",
          p: 2,
          mb: 2,
        }}
      >
        <Typography fontWeight={700} color={darkText}>
          Profile: {t.name || profile?.profileName || "Custom Profile"}
        </Typography>
        <Typography sx={{ color: darkText }}>
          Temp: {temp[0]}–{temp[1]}°F
        </Typography>
        <Typography sx={{ color: darkText }}>
          Precipitation: {t.precip || "—"}
        </Typography>
        <Typography sx={{ color: darkText }}>
          Max wind speed: {wind} mph
        </Typography>
        <Typography sx={{ color: darkText }}>
          Cloud cover: {t.clouds || t.cloud || "—"}
        </Typography>
        <Typography sx={{ color: darkText }}>
          Min AQI: {t.minAQI || t.aqi || "—"}
        </Typography>
        <Typography sx={{ color: darkText }}>
          Max humidity: {t.maxHumidity || t.humidity || "—"}
        </Typography>
      </Box>

      {/* --- DATES --- */}
      <Box
        sx={{
          backgroundColor: lightBg,
          borderRadius: "12px",
          p: 2,
          mb: 3,
        }}
      >
        <Typography fontWeight={700} color={darkText}>
          Dates
        </Typography>
        <Typography color={darkText}>
          {start} → {end}
        </Typography>
      </Box>

      <Divider sx={{ mb: 3 }} />

      {/* --- BUTTONS --- */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Button
          variant="contained"
          onClick={onBack}
          disabled={loading}
          sx={{
            backgroundColor: gold,
            color: "#000",
            borderRadius: "12px",
            textTransform: "none",
            fontWeight: 600,
            px: 4,
            py: 1,
            "&:hover": { backgroundColor: "#F3CD52" },
          }}
        >
          Back
        </Button>

        <Button
          variant="contained"
          disabled={loading}
          sx={{
            backgroundColor: loading ? "#9AAEF7" : "#3366FF",
            color: "#fff",
            borderRadius: "20px",
            textTransform: "none",
            fontWeight: 600,
            px: 6,
            py: 1.4,
            "&:hover": { backgroundColor: "#2B57E0" },
          }}
          onClick={handleSubmit}
        >
          {loading ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <CircularProgress size={18} color="inherit" />
              Sending...
            </Box>
          ) : (
            "SHOW ME MY REPORT!"
          )}
        </Button>
      </Box>
    </Paper>
  );
}
