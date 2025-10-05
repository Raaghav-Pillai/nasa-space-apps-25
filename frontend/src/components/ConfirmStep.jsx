import React from "react";
import { Box, Typography, Paper, Button, Divider } from "@mui/material";

export default function ConfirmStep({ location, profile, dates, onBack }) {
  // Colors
  const gold = "#F6D76F";
  const lightBg = "#FAF9F6";
  const darkText = "#615b40";

  // --- Extract data safely ---
  const t = profile?.traits || {};
  const temp = t.tempRange || t.temperature || ["—", "—"];
  const wind = t.windMaxMph || t.wind || "—";

// --- Format location ---
const hasLocation = location?.city;
const locationText = hasLocation
  ? `${location.city}${location.region ? ", " + location.region : ""}${
      location.coordinates
        ? `\n${location.coordinates.lat.toFixed(4)}° N, ${location.coordinates.lng.toFixed(4)}° W`
        : ""
    }`
  : "—";

  // --- Format date range ---
  const start = dates?.startDate
    ? `${dates.startDate} ${dates.startTime || "00:00:00"}`
    : "—";
  const end = dates?.endDate
    ? `${dates.endDate} ${dates.endTime || "23:59:59"}`
    : "—";

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
      <Typography
        variant="h6"
        fontWeight={700}
        color={darkText}
        sx={{ mb: 2 }}
      >
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
        <Typography sx={{ color: darkText }}>Temp: {temp[0]}–{temp[1]}°F</Typography>
        <Typography sx={{ color: darkText }}>Precipitation: {t.precip || "—"}</Typography>
        <Typography sx={{ color: darkText }}>Max wind speed: {wind} mph</Typography>
        <Typography sx={{ color: darkText }}>Cloud cover: {t.clouds || t.cloud || "—"}</Typography>
        <Typography sx={{ color: darkText }}>Min AQI: {t.minAQI || t.aqi || "—"}</Typography>
        <Typography sx={{ color: darkText }}>Max humidity: {t.maxHumidity || t.humidity || "—"}</Typography>
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
          sx={{
            backgroundColor: "#F3CD52",
            color: "#fff",
            borderRadius: "20px",
            textTransform: "none",
            fontWeight: 600,
            px: 6,
            py: 1.4,
            "&:hover": { backgroundColor: "#F3CD52" },
          }}
          onClick={() => alert("Report generation coming soon!")}
        >
          SHOW ME MY REPORT!
        </Button>
      </Box>
    </Paper>
  );
}
