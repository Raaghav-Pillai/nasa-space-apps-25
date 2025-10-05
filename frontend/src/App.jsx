import React, { useState } from "react";
import { Box, Container } from "@mui/material";
import StepIndicator from "./components/StepIndicator.jsx";
import LocationStep from "./components/LocationStep.jsx";
import ProfileStep from "./components/ProfileStep.jsx";
import DatesStep from "./components/DatesStep.jsx";
import ConfirmStep from "./components/ConfirmStep.jsx";

export default function App() {
  // Track which step we're on
  const [step, setStep] = useState(0);

  // Initialize location, profile, and dates objects
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

  // Navigation helpers
  const nextStep = () => setStep((prev) => Math.min(prev + 1, 3));
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 0));

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Top horizontal step indicator */}
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
              // ✅ Unwrap payload so ConfirmStep reads correctly
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
  );
}
