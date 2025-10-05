import React, { useState } from "react";
import { Box, Container } from "@mui/material";
import StepIndicator from "./components/StepIndicator.jsx";
import LocationStep from "./components/LocationStep.jsx";
import ProfileStep from "./components/ProfileStep.jsx";
import DatesStep from "./components/DatesStep.jsx";
import ConfirmStep from "./components/ConfirmStep.jsx";

export default function App() {
  const [step, setStep] = useState(0);

  const [location, setLocation] = useState({
    city: "",
    coordinates: null,
  });

  const [profile, setProfile] = useState(null);

  const [dates, setDates] = useState({
    subPage: "choice",
    mode: "single",
    startDate: "",
    endDate: "",
    startTime: "",
    endTime: "",
    general: null,
  });

  const nextStep = () => setStep((prev) => Math.min(prev + 1, 3));
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 0));

  return (
    // Full white background
    <Box sx={{ backgroundColor: "#FFFFFF", minHeight: "100vh", py: 4 }}>
      {/* White container */}
      <Container
        maxWidth="md"
        sx={{
          py: 4,
          borderRadius: "16px",
          backgroundColor: "#FFFFFF",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.05)",
        }}
      >
        <StepIndicator activeStep={step} />

        <Box sx={{ mt: 4 }}>
          {step === 0 && (
            <LocationStep
              location={location}
              setLocation={setLocation}
              onNext={nextStep}
            />
          )}

          {step === 1 && (
            <ProfileStep
              onNext={(data) => {
                if (data?.profile) {
                  setProfile(data.profile);
                } else {
                  setProfile(data);
                }
                nextStep();
              }}
              onBack={prevStep}
            />
          )}

          {step === 2 && (
            <DatesStep
              dates={dates}
              setDates={setDates}
              onBack={prevStep}
              onNext={nextStep}
            />
          )}

          {step === 3 && (
            <ConfirmStep
              location={location}
              profile={profile}
              dates={dates}
              onBack={prevStep}
            />
          )}
        </Box>
      </Container>
    </Box>
  );
}
