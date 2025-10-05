import React from "react";
import { Box, Typography } from "@mui/material";
import { Star } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function StepIndicator({ activeStep }) {
  const steps = ["Location", "Profile", "Dates", "Confirm"];

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#fefcf4ff",
        borderRadius: "16px",
        p: 1,
        boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
        position: "relative",
      }}
    >
      {/* Animated background pill */}
      <Box
        sx={{
          position: "absolute",
          top: 6,
          bottom: 6,
          left: `${activeStep * 25}%`,
          width: "25%",
          borderRadius: "12px",
          backgroundColor: "#F6D76F",
          transition: "left 0.4s cubic-bezier(0.25, 1, 0.5, 1)",
          zIndex: 1,
        }}
      />

      {steps.map((label, index) => {
        const isActive = index === activeStep;

        return (
          <Box
            key={label}
            sx={{
              flex: 1,
              position: "relative",
              borderRadius:
                index === 0
                  ? "12px 0 0 12px"
                  : index === steps.length - 1
                  ? "0 12px 12px 0"
                  : 0,
              backgroundColor: "transparent",
              color: isActive ? "#ffffffff" : "#8A8A8A",
              textTransform: "none",
              fontWeight: 700,
              py: 1.8,
              transition: "color 0.2s ease-in-out",
              pointerEvents: "none", // disable clicks
              zIndex: 2, // sits above pill
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
              <Star
                size={16}
                fill={isActive ? "#faf6d1ff" : "#c4c2c2ff"}
                color={isActive ? "#faf6d1ff" : "#c4c2c2ff"}
              />
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  fontFamily: "Roboto, sans-serif",
                  letterSpacing: "0.02em",
                  color: isActive ? "#ffffffff" : "#8A8A8A",
                }}
              >
                {label}
              </Typography>
            </Box>
          </Box>
        );
      })}
    </Box>
  );
}
