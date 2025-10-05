import React from "react";
import { Box, Typography, Paper, Button, Divider, Stack } from "@mui/material";

// Example icons — replace these with your own asset paths
import LocationIcon from "../assets/placeholder.jpg";
import ProfileIcon from "../assets/placeholder.jpg";
import CalendarIcon from "../assets/placeholder.jpg";

export default function ConfirmStep({ location, profile, dates, onBack }) {
  const gold = "#F6D76F";
  const lightBg = "#FAF9F6";
  const darkText = "#615b40";

  // --- Extract data safely ---
  const t = profile?.traits || {};
  const temp = t.tempRange || t.temperature || ["—", "—"];
  const wind = t.windMaxMph || t.wind || "—";

  // --- Format location for display ---
  const hasLocation = location?.city || location?.coordinates;
  const locationText = hasLocation
    ? `${location.city || "—"}${
        location.region ? ", " + location.region : ""
      }${
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

  // --- Bundle all data for backend ---
  const packagedData = {
    location: {
      city: location.city || null,
      region: location.region || null,
      coordinates: location.coordinates || null,
    },
    profile: {
      name: t.name || profile?.profileName || "Custom Profile",
      temperature: temp,
      precip: t.precip || null,
      windMaxMph: wind,
      clouds: t.clouds || t.cloud || null,
      minAQI: t.minAQI || t.aqi || null,
      maxHumidity: t.maxHumidity || t.humidity || null,
    },
    dates: {
      startDate: dates.startDate,
      endDate: dates.endDate,
      startTime: dates.startTime,
      endTime: dates.endTime,
    },
  };

  // --- Submit function ---
  const handleSubmit = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(packagedData),
      });

      if (!response.ok) throw new Error("Failed to send data");

      const result = await response.json();
      console.log("✅ Successfully sent data:", result);
      alert("Report generated successfully!");
    } catch (error) {
      console.error("❌ Error sending data:", error);
      alert("An error occurred while sending your data.");
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
      <Typography
        variant="h5"
        fontWeight={700}
        color={darkText}
        textAlign="center"
        sx={{ mb: 2 }}
      >
        Confirm your selection!
      </Typography>

      {/* --- OUTER WRAPPER --- */}
      <Box
        sx={{
          backgroundColor: "#F8F6F1",
          borderRadius: "20px",
          p: 3,
          display: "flex",
          flexDirection: "column",
          gap: 2.5,
        }}
      >
        {/* --- LOCATION --- */}
        <InfoRow
          icon={LocationIcon}
          bg={lightBg}
          title="Location"
          content={locationText}
          darkText={darkText}
        />

        {/* --- PROFILE --- */}
        <InfoRow
          icon={ProfileIcon}
          bg={gold}
          title={`Profile: ${t.name || profile?.profileName || "Custom Profile"}`}
          content={
            <>
              Temp: {temp[0]}–{temp[1]}°F
              <br />
              Precipitation: {t.precip || "—"}
              <br />
              Max wind speed: {wind} mph
              <br />
              Cloud cover: {t.clouds || t.cloud || "—"}
              <br />
              Min AQI: {t.minAQI || t.aqi || "—"}
              <br />
              Max humidity: {t.maxHumidity || t.humidity || "—"}
            </>
          }
          darkText={darkText}
        />

        {/* --- DATES --- */}
        <InfoRow
          icon={CalendarIcon}
          bg={lightBg}
          title="Dates"
          content={`${start} → ${end}`}
          darkText={darkText}
        />
      </Box>

      <Divider sx={{ my: 3 }} />

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
            fontWeight: 700,
            px: 4,
            py: 1,
            "&:hover": { backgroundColor: "#C2A64C", color: "#fff" },
          }}
        >
          Back
        </Button>

        <Button
          variant="contained"
          onClick={handleSubmit}
          sx={{
            backgroundColor: gold,
            color: "#000",
            borderRadius: "12px",
            textTransform: "none",
            fontWeight: 700,
            px: 6,
            py: 1.4,
            "&:hover": { backgroundColor: "#B69944", color: "#fff"},
          }}
        >
          SHOW ME MY REPORT!
        </Button>
      </Box>
    </Paper>
  );
}

/* --- InfoRow Component with Icon Left + Box Right --- */
function InfoRow({ icon, title, content, bg, darkText }) {
  return (
    <Stack
      direction="row"
      alignItems="center"
      spacing={2}
      sx={{
        backgroundColor: bg,
        borderRadius: "12px",
        p: 2,
      }}
    >
      <Box
        component="img"
        src={icon}
        alt={`${title} icon`}
        sx={{
          width: 40,
          height: 40,
          opacity: 0.9,
          flexShrink: 0,
        }}
      />
      <Box>
        <Typography fontWeight={700} color={darkText}>
          {title}
        </Typography>
        <Typography sx={{ color: darkText, whiteSpace: "pre-line" }}>
          {content}
        </Typography>
      </Box>
    </Stack>
  );
}
