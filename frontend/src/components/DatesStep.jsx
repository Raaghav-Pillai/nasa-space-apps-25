import React, { useEffect, useState } from 'react';
import dayjs from 'dayjs';
import {
  Box,
  Button,
  Stack,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { DatePicker, TimePicker } from '@mui/x-date-pickers';
import { computeGeneralPeriod, timeToHHMMSS } from '../utils/dateUtils.js';

export default function DatesStep({ dates, setDates, onBack, onNext }) {
  useEffect(() => {
    if (!dates || !dates.subPage) {
      setDates((prev) => {
        if (prev?.subPage) return prev;
        return { ...prev, subPage: 'choice', mode: 'single' };
      });
    }
  }, [dates, setDates]);

  const goto = (subPage) => setDates((prev) => ({ ...prev, subPage }));

  const gold = '#ebcb6b';
  const goldHover = '#e1c25c';
  const darkText = '#615b40';

  /* ---------------- PAGE 4: CHOICE ---------------- */
  const Page4Choice = () => (
    <CenteredBox>
      <Typography variant="h6" fontWeight={700} color={darkText} textAlign="center">
        Would you like to plan for one day or multiple?
      </Typography>
      <Stack direction="row" spacing={3}>
        <GoldButton onClick={() => goto('single')}>Just one!</GoldButton>
        <GoldButton onClick={() => goto('specific')}>Multiple!</GoldButton>
      </Stack>
    </CenteredBox>
  );

  /* ---------------- PAGE 5: SPECIFIC ---------------- */
  const Page5Specific = () => {
    const [start, setStart] = useState(dates.startDate ? dayjs(dates.startDate) : null);
    const [end, setEnd] = useState(dates.endDate ? dayjs(dates.endDate) : null);
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
      if (!start || !end) return alert('Please pick both start and end dates.');
      setDates((prev) => ({
        ...prev,
        startDate: start.format('YYYY-MM-DD'),
        endDate: end.format('YYYY-MM-DD'),
        startTime: '00:00:00',
        endTime: '23:59:59',
        mode: 'multi',
      }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    };

    return (
      <CenteredBox>
        <Typography variant="h6" fontWeight={700} color={darkText}>
          Select your date range!
        </Typography>
        <Stack direction="row" spacing={2} mt={2}>
          <DatePicker
            label="From"
            value={start}
            onChange={(v) => {
              setStart(v);
              setSaved(false);
            }}
            slotProps={{ textField: { fullWidth: true } }}
          />
          <DatePicker
            label="To"
            value={end}
            onChange={(v) => {
              setEnd(v);
              setSaved(false);
            }}
            slotProps={{ textField: { fullWidth: true } }}
          />
        </Stack>

        <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mt: 3 }}>
          <GoldButton onClick={handleSave}>Save</GoldButton>
          <Typography
  variant="body1"
  sx={{
    color: '#2e7d32',
    fontWeight: 600,
    transition: 'opacity 0.4s ease',
    opacity: saved ? 1 : 0,
  }}
>
  {'\u2713'} Saved
</Typography>

        </Stack>

        <Stack direction="row" spacing={2} mt={2}>
          <Button variant="outlined" onClick={() => goto('general')} sx={{ borderColor: gold, color: darkText }}>
            General options
          </Button>
          <Button variant="outlined" onClick={() => goto('single')} sx={{ borderColor: gold, color: darkText }}>
            Just one day
          </Button>
        </Stack>
      </CenteredBox>
    );
  };

  /* ---------------- PAGE 6: GENERAL ---------------- */
  const Page6General = () => {
    const today = dayjs();
    const [period, setPeriod] = useState(dates.general?.period || 'first_week');
    const [monthIndex, setMonthIndex] = useState(dates.general?.monthIndex ?? today.month());
    const [year, setYear] = useState(dates.general?.year ?? today.year());
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
      const { start, end } = computeGeneralPeriod(period, monthIndex, year);
      setDates((prev) => ({
        ...prev,
        general: { period, monthIndex, year },
        startDate: start,
        endDate: end,
        startTime: '00:00:00',
        endTime: '23:59:59',
        mode: 'multi',
      }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    };

    return (
      <CenteredBox>
        <Typography variant="h6" fontWeight={700} color={darkText}>
          Choose a general time period!
        </Typography>

        <Stack direction="row" spacing={2} mt={2} justifyContent="center" flexWrap="wrap">
          <FormControl sx={{ minWidth: 190 }}>
            <InputLabel id="period-label">Period</InputLabel>
            <Select
              labelId="period-label"
              value={period}
              label="Period"
              onChange={(e) => {
                setPeriod(e.target.value);
                setSaved(false);
              }}
            >
              <MenuItem value="first_week">First week of</MenuItem>
              <MenuItem value="second_week">Second week of</MenuItem>
              <MenuItem value="third_week">Third week of</MenuItem>
              <MenuItem value="last_week">Last week of</MenuItem>
              <MenuItem value="first_2_weeks">First two weeks of</MenuItem>
              <MenuItem value="last_2_weeks">Last two weeks of</MenuItem>
              <MenuItem value="full_month">Full month of</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 160 }}>
            <InputLabel id="month-label">Month</InputLabel>
            <Select
              labelId="month-label"
              value={monthIndex}
              label="Month"
              onChange={(e) => {
                setMonthIndex(Number(e.target.value));
                setSaved(false);
              }}
            >
              {Array.from({ length: 12 }).map((_, i) => (
                <MenuItem key={i} value={i}>
                  {dayjs().month(i).format('MMMM')}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel id="year-label">Year</InputLabel>
            <Select
              labelId="year-label"
              value={year}
              label="Year"
              onChange={(e) => {
                setYear(Number(e.target.value));
                setSaved(false);
              }}
            >
              {[today.year(), today.year() + 1, today.year() + 2].map((y) => (
                <MenuItem key={y} value={y}>
                  {y}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>

        <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mt: 3 }}>
          <GoldButton onClick={handleSave}>Save</GoldButton>
         <Typography
  variant="body1"
  sx={{
    color: '#2e7d32',
    fontWeight: 600,
    transition: 'opacity 0.4s ease',
    opacity: saved ? 1 : 0,
  }}
>
  {'\u2713'} Saved
</Typography>

        </Stack>

        <Stack direction="row" spacing={2} mt={3}>
          <Button variant="outlined" onClick={() => goto('specific')} sx={{ borderColor: gold, color: darkText }}>
            Specific dates
          </Button>
          <Button variant="outlined" onClick={() => goto('single')} sx={{ borderColor: gold, color: darkText }}>
            Just one day
          </Button>
        </Stack>
      </CenteredBox>
    );
  };

  /* ---------------- PAGE 7: SINGLE ---------------- */
  const Page7Single = () => {
    const [date, setDate] = useState(dates.startDate ? dayjs(dates.startDate) : null);
    const [time, setTime] = useState(
      dates.startTime ? dayjs(`1970-01-01T${dates.startTime}`) : dayjs().hour(12).minute(0).second(0)
    );
    const [saved, setSaved] = useState(false);

    const handleSave = () => {
      if (!date) return alert('Please pick a date.');
      setDates((prev) => ({
        ...prev,
        startDate: date.format('YYYY-MM-DD'),
        startTime: timeToHHMMSS(time.format('HH:mm:ss')),
        endDate: date.format('YYYY-MM-DD'),
        endTime: timeToHHMMSS(time.format('HH:mm:ss')),
        mode: 'single',
      }));
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    };

    return (
      <CenteredBox>
        <Typography variant="h6" fontWeight={700} color={darkText}>
          Select your date and time!
        </Typography>
        <Stack direction="row" spacing={2} mt={2} alignItems="flex-end">
          <DatePicker
            label="Date"
            value={date}
            onChange={(v) => {
              setDate(v);
              setSaved(false);
            }}
            slotProps={{ textField: { fullWidth: true } }}
          />
          <TimePicker
            label="Time"
            value={time}
            onChange={(v) => {
              setTime(v);
              setSaved(false);
            }}
            views={['hours', 'minutes', 'seconds']}
            slotProps={{ textField: { fullWidth: true } }}
          />
        </Stack>

        <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mt: 3 }}>
          <GoldButton onClick={handleSave}>Save</GoldButton>
          <Typography
  variant="body1"
  sx={{
    color: '#2e7d32',
    fontWeight: 600,
    transition: 'opacity 0.4s ease',
    opacity: saved ? 1 : 0,
  }}
>
  {'\u2713'} Saved
</Typography>

        </Stack>

        <Button
          variant="outlined"
          sx={{ mt: 2, borderColor: gold, color: darkText }}
          onClick={() => goto('specific')}
        >
          I’d like to pick a range
        </Button>
      </CenteredBox>
    );
  };

  /* ---------------- RENDER ---------------- */
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '80vh', justifyContent: 'space-between' }}>
      <Box sx={{ flexGrow: 1 }}>
        {dates.subPage === 'choice' && <Page4Choice />}
        {dates.subPage === 'specific' && <Page5Specific />}
        {dates.subPage === 'general' && <Page6General />}
        {dates.subPage === 'single' && <Page7Single />}
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <GoldButton onClick={onBack}>Back</GoldButton>
        <GoldButton
          onClick={onNext}
          disabled={!dates.startDate || !dates.endDate}
          sx={{
            opacity: !dates.startDate || !dates.endDate ? 0.6 : 1,
            cursor: !dates.startDate || !dates.endDate ? 'not-allowed' : 'pointer',
          }}
        >
          Next
        </GoldButton>
      </Box>
    </Box>
  );

  /* ---------------- Reusable components ---------------- */
  function CenteredBox({ children }) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          minHeight: '70vh',
          gap: 3,
        }}
      >
        {children}
      </Box>
    );
  }

  function GoldButton({ children, sx, ...props }) {
    return (
      <Button
        variant="contained"
        sx={{
          backgroundColor: gold,
          color: '#fff',
          borderRadius: 2,
          px: 4,
          py: 1.2,
          textTransform: 'none',
          fontWeight: 500,
          '&:hover': { backgroundColor: goldHover },
          ...sx,
        }}
        {...props}
      >
        {children}
      </Button>
    );
  }
}
