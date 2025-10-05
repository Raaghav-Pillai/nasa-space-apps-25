import React from "react";
import { Box, Typography } from "@mui/material";
import { motion } from "framer-motion";

/**
 * Figma-accurate Step Bar
 * - Equal-width tabs
 * - Active tab = #F6D76F background, black text
 * - Inactive tabs = #F9F8F4 background, gray text
 * - Smooth animated highlight bar across the top
 * - Rounded ends + subtle elevation
 */

const steps = ["Location", "Profile", "Dates", "Confirm"];

export default function StepIndicator({ activeStep }) {
  const stepWidth = 100 / steps.length;

  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        borderRadius: "12px",
        boxShadow: "0px 1px 3px rgba(0,0,0,0.1)",
        overflow: "hidden",
        backgroundColor: "#F9F8F4",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      {/* Animated yellow background */}
      <motion.div
        layout
        initial={false}
        animate={{
          left: `${activeStep * stepWidth}%`,
        }}
        transition={{
          type: "spring",
          stiffness: 350,
          damping: 35,
        }}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: `${stepWidth}%`,
          height: "100%",
          backgroundColor: "#F6D76F",
          borderRadius: "12px",
          zIndex: 0,
        }}
      />

      {/* Step labels */}
      {steps.map((label, index) => {
        const isActive = index === activeStep;
        const isFirst = index === 0;
        const isLast = index === steps.length - 1;

        return (
          <Box
            key={label}
            sx={{
              flex: 1,
              textAlign: "center",
              py: 1.5,
              position: "relative",
              borderRight:
                index !== steps.length - 1
                  ? "1px solid rgba(0,0,0,0.07)"
                  : "none",
              borderTopLeftRadius: isFirst ? "12px" : 0,
              borderBottomLeftRadius: isFirst ? "12px" : 0,
              borderTopRightRadius: isLast ? "12px" : 0,
              borderBottomRightRadius: isLast ? "12px" : 0,
              zIndex: 1,
            }}
          >
            <Typography
              variant="body1"
              sx={{
                color: isActive ? "#000000" : "#6F6F6F",
                fontWeight: isActive ? 600 : 500,
                fontFamily: '"Roboto","Noto Sans",sans-serif',
                letterSpacing: 0.15,
                userSelect: "none",
                transition: "color 0.3s ease",
              }}
            >
              {label}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
}
