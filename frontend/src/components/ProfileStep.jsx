import React, { useState } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Button,
  Slider,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Divider,
} from "@mui/material";

/* --------------------------------------------------------------------------
 *  ProfileStep.jsx
 *  - Preset + Custom editor flow
 *  - Seamless numeric updates (no fade)
 *  - Floating white card (elevation=6)
 *  - Matches Figma layout, M3 colors, and typography
 * -------------------------------------------------------------------------- */

const PRESETS = [
  { id: "beach", name: "Beach Day", desc: "Prefers warm, sunny conditions." },
  { id: "hiking", name: "Hiking", desc: "Prefers mid-temperature, cloudy conditions." },
  { id: "skiing", name: "Skiing", desc: "Prefers cold, mild conditions." },
  { id: "rain", name: "Rain Dancing", desc: "Prefers mid-temperature, rainy conditions." },
  { id: "sailing", name: "Sailing", desc: "Prefers warm, windy conditions." },
  { id: "custom", name: "Custom", desc: "Create your own conditions!" },
];

const presetDefaults = {
  beach: { temperature: [75, 95], precip: "none", wind: 25, cloud: "clear", aqi: 70, humidity: 70, name: "Beach Day" },
  hiking: { temperature: [55, 75], precip: "drizzle", wind: 20, cloud: "light", aqi: 60, humidity: 60, name: "Hiking" },
  skiing: { temperature: [20, 40], precip: "any", wind: 35, cloud: "cloudy", aqi: 50, humidity: 80, name: "Skiing" },
  rain: { temperature: [60, 75], precip: "any", wind: 15, cloud: "cloudy", aqi: 70, humidity: 100, name: "Rain Dancing" },
  sailing: { temperature: [65, 85], precip: "none", wind: 40, cloud: "clear", aqi: 80, humidity: 70, name: "Sailing" },
};

function NumberTag({ n }) {
  return (
    <Box
      sx={{
        width: 22,
        height: 22,
        borderRadius: "50%",
        backgroundColor: "#E9C64F",
        color: "#000",
        fontWeight: 700,
        fontSize: "0.75rem",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        mr: 1,
      }}
    >
      {n}
    </Box>
  );
}

function MutedLabel({ children }) {
  return (
    <Typography
      variant="body2"
      sx={{ color: "#5F5F5F", display: "flex", justifyContent: "space-between" }}
    >
      {children}
    </Typography>
  );
}

export default function ProfileStep({ onBack, onNext }) {
  const [selected, setSelected] = useState(null);
  const [customMode, setCustomMode] = useState(false);
  const [custom, setCustom] = useState({
    temperature: [60, 80],
    precip: "none",
    wind: 15,
    cloud: "clear",
    aqi: 50,
    humidity: 50,
    name: "",
  });

  const handleSelectPreset = (p) => {
    setSelected(p);

    // Always initialize with default values first
    if (presetDefaults[p.id]) {
      setCustom((prev) => ({ ...prev, ...presetDefaults[p.id] }));
    }

    // Delay switching mode slightly to prevent state conflict
    if (p.id === "custom") {
      setTimeout(() => setCustomMode(true), 0);
    } else {
      setCustomMode(false);
    }
  };

  const goToPresets = () => setCustomMode(false);

  const saveCustom = () => {
    const payload = {
      profile: {
        presetId: selected?.id || "custom",
        traits: {
          name: custom.name || presetDefaults[selected?.id]?.name || "Custom Profile",
          tempRange: custom.temperature,
          precip: custom.precip,
          windMaxMph: custom.wind,
          clouds: custom.cloud,
          minAQI: custom.aqi,
          maxHumidity: custom.humidity,
        },
      },
    };
    console.log("Profile payload →", payload);
    onNext?.(payload);
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
      {!customMode ? (
        /* ---------------- PRESET GRID ---------------- */
        <Box sx={{ width: "100%" }}>
          <Typography variant="h5" sx={{ fontWeight: 700, textAlign: "center", mb: 2 }}>
            Select an Activity!
          </Typography>

{/* --- Card Grid --- */}
<Box
  sx={{
    width: "100%",
    maxWidth: 1200, // slightly wider container for visual balance
    mx: "auto",
    display: "flex",
    justifyContent: "center",
  }}
>
  <Grid
    container
    spacing={3}
    justifyContent="center"
    alignItems="stretch"
    sx={{
      width: "100%",
      maxWidth: 1100,
    }}
  >
    {PRESETS.map((p, idx) => {
      const isActive = selected?.id === p.id;
      return (
        <Grid
          item
          key={p.id}
          sx={{
            flex: "0 0 31%", // ✅ consistent width for all cards (3 per row)
            display: "flex",
            justifyContent: "center",
            alignItems: "stretch",
          }}
        >
          <Paper
            elevation={isActive ? 6 : 2}
            onClick={() => handleSelectPreset(p)}
            sx={{
              cursor: "pointer",
              width: "100%",
              height: 320, // ✅ fixed height for perfect vertical alignment
              borderRadius: "12px",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              alignItems: "stretch",
              backgroundColor: "#F3EFE6",
              border: isActive
                ? "2px solid #42360eff"
                : "1px solid rgba(0,0,0,0.12)",
              transition: "all 0.25s ease",
            }}
          >
            {/* Header */}
            <Box
              sx={{
                backgroundColor: "#F3EEDD",
                py: 1.5,
                px: 1.2,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderBottom: "1px solid rgba(0,0,0,0.08)",
                minHeight: 56,
              }}
            >
              <NumberTag n={idx + 1} />
              <Typography
                variant="title3"
                sx={{
                  fontWeight: 720,
                  textAlign: "center",
                  color: "#000",
                  lineHeight: 1,
                }}
              >
                {p.name}
              </Typography>
            </Box>

            {/* Visuals */}
            <Box
              sx={{
                flexGrow: 1,
                backgroundColor: "#E9E6EF",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                gap: 1.5,
              }}
            >
              <Box sx={{ width: 26, height: 26, backgroundColor: "#C7C2CC", borderRadius: "6px" }} />
              <Box sx={{ width: 30, height: 30, backgroundColor: "#C7C2CC", borderRadius: "50%" }} />
              <Box
                sx={{
                  width: 26,
                  height: 26,
                  backgroundColor: "#C7C2CC",
                  clipPath: "polygon(50% 0%, 0% 100%, 100% 100%)",
                }}
              />
            </Box>

            {/* Footer */}
            <Box
              sx={{
                backgroundColor: "#F3EFE6",
                textAlign: "center",
                py: 1.6,
                px: 1.5,
                minHeight: 60,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Typography
                variant="body2"
                sx={{
                  color: "#333",
                  fontWeight: 600,
                  lineHeight: 1.4,
                  fontSize: "0.9rem",
                }}
              >
                {p.desc}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      );
    })}
  </Grid>
</Box>

{/* Navigation buttons for preset page */}
<Box sx={{ display: "flex", justifyContent: "space-between", mt: 3 }}>
  <Button
    variant="contained"
    onClick={onBack}
    sx={{
      backgroundColor: "#F6D76F",
      color: "#000",
      borderRadius: "12px",
      textTransform: "none",
      fontWeight: 600,
      px: 4,
      py: 1,
      "&:hover": { backgroundColor: "#C2A64C", color: "#fff" },
    }}
  >
    Back
  </Button>

  <Button
    variant="contained"
    disabled={!selected}
    onClick={() => {
      if (!selected) return;

      // If custom selected → go to editor
      if (selected.id === "custom") {
        setCustomMode(true);
        return;
      }

      // Otherwise, send preset data payload
      const def = presetDefaults[selected.id];
      const payload = {
        profile: {
          presetId: selected.id,
          traits: {
            name: def.name,
            tempRange: def.temperature,
            precip: def.precip,
            windMaxMph: def.wind,
            clouds: def.cloud,
            minAQI: def.aqi,
            maxHumidity: def.humidity,
          },
        },
      };
      console.log("Preset payload →", payload);
      onNext?.(payload);
    }}
    sx={{
      backgroundColor: selected ? "#F6D76F" : "#DADADA",
      color: "#000",
      borderRadius: "12px",
      textTransform: "none",
      fontWeight: 600,
      px: 4,
      py: 1,
      "&:hover": {
        backgroundColor: selected ? "#F3CD52" : "#DADADA",
      },
    }}
  >
    Next
  </Button>
</Box>
        </Box>
      ) : (
        /* ---------------- CUSTOM EDITOR ---------------- */
        <Box sx={{ width: "100%" }}>
          <Typography variant="h5" sx={{ fontWeight: 700, textAlign: "center", mb: 3 }}>
            Create your profile...
          </Typography>

          {/* Temperature */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <NumberTag n={1} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Ideal Temperature Range (°F):
              </Typography>
              <span style={{ marginLeft: 8, fontWeight: 500 }}>
                {custom.temperature[0]}–{custom.temperature[1]}°F
              </span>
            </Box>
            <Slider
              value={custom.temperature}
              onChange={(_, val) => setCustom((p) => ({ ...p, temperature: val }))}
              min={0}
              max={110}
              sx={{ color: "#F6D76F" }}
            />
            <MutedLabel>
              <span>0</span>
              <span>110</span>
            </MutedLabel>
          </Box>

          {/* Precipitation */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <NumberTag n={2} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Precipitation:
              </Typography>
            </Box>
            <RadioGroup
              row
              value={custom.precip}
              onChange={(e) => setCustom((p) => ({ ...p, precip: e.target.value }))}
            >
              <FormControlLabel value="none" control={<Radio />} label="No chances of rain!" />
              <FormControlLabel value="drizzle" control={<Radio />} label="A drizzle is okay." />
              <FormControlLabel value="any" control={<Radio />} label="Any conditions!" />
            </RadioGroup>
            <MutedLabel>Selected: {custom.precip}</MutedLabel>
          </Box>

          {/* Wind */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <NumberTag n={3} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Max Wind Speed:
              </Typography>
              <span style={{ marginLeft: 8, fontWeight: 500 }}>{custom.wind} mph</span>
            </Box>
            <Slider
              value={custom.wind}
              onChange={(_, val) => setCustom((p) => ({ ...p, wind: val }))}
              min={0}
              max={50}
              sx={{ color: "#F6D76F" }}
            />
            <MutedLabel>
              <span>0</span>
              <span>50</span>
            </MutedLabel>
          </Box>

          {/* Cloud Cover */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <NumberTag n={4} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Cloud Cover:
              </Typography>
            </Box>
            <RadioGroup
              row
              value={custom.cloud}
              onChange={(e) => setCustom((p) => ({ ...p, cloud: e.target.value }))}
            >
              <FormControlLabel value="clear" control={<Radio />} label="Clear skies only" />
              <FormControlLabel value="light" control={<Radio />} label="Lightly Cloudy" />
              <FormControlLabel value="cloudy" control={<Radio />} label="Cloudy" />
              <FormControlLabel value="any" control={<Radio />} label="Any conditions!" />
            </RadioGroup>
            <MutedLabel>Selected: {custom.cloud}</MutedLabel>
          </Box>

          {/* Air Quality */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <NumberTag n={5} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Minimum Air Quality:
              </Typography>
              <span style={{ marginLeft: 8, fontWeight: 500 }}>{custom.aqi}</span>
            </Box>
            <Slider
              value={custom.aqi}
              onChange={(_, val) => setCustom((p) => ({ ...p, aqi: val }))}
              min={0}
              max={100}
              sx={{ color: "#F6D76F" }}
            />
            <MutedLabel>
              <span>0</span>
              <span>100</span>
            </MutedLabel>
          </Box>

          {/* Humidity */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
              <NumberTag n={6} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Max Humidity:
              </Typography>
              <span style={{ marginLeft: 8, fontWeight: 500 }}>{custom.humidity}%</span>
            </Box>
            <Slider
              value={custom.humidity}
              onChange={(_, val) => setCustom((p) => ({ ...p, humidity: val }))}
              min={0}
              max={100}
              sx={{ color: "#F6D76F" }}
            />
            <MutedLabel>
              <span>0</span>
              <span>100</span>
            </MutedLabel>
          </Box>

          <Divider sx={{ my: 1.5 }} />
          <TextField
            fullWidth
            placeholder="My perfect hike..."
            label="Save as"
            value={custom.name}
            onChange={(e) => setCustom((p) => ({ ...p, name: e.target.value }))}
            sx={{
              mt: 1,
              "& .MuiOutlinedInput-root": { borderRadius: "12px", backgroundColor: "#FAF9F6" },
            }}
          />

          {/* Footer Buttons */}
          <Box sx={{ display: "flex", justifyContent: "space-between", mt: 3 }}>
            <Button
              variant="contained"
              onClick={onBack}
              sx={{
                backgroundColor: "#F6D76F",
                color: "#000",
                borderRadius: "12px",
                textTransform: "none",
                fontWeight: 600,
                px: 4,
                py: 1,
                mr: 2,
                "&:hover": { backgroundColor: "#F3CD52" },
              }}
            >
              Back
            </Button>

            <Button
              variant="contained"
              onClick={goToPresets}
              sx={{
                backgroundColor: "#D5C59C",
                color: "#000",
                borderRadius: "12px",
                textTransform: "none",
                fontWeight: 600,
                px: 4,
                py: 1,
                mx: 2,
                "&:hover": { backgroundColor: "#CDBB8D" },
              }}
            >
              Presets
            </Button>

            <Button
              variant="contained"
              onClick={saveCustom}
              sx={{
                backgroundColor: "#F6D76F",
                color: "#000",
                borderRadius: "12px",
                textTransform: "none",
                fontWeight: 600,
                px: 4,
                py: 1,
                ml: 2,
                "&:hover": { backgroundColor: "#F3CD52" },
              }}
            >
              Next
            </Button>
          </Box>
        </Box>
      )}
    </Paper>
  );
}
