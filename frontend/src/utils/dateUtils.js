export const pad2 = (n) => n.toString().padStart(2, '0');

export const timeToHHMMSS = (t) => {
  if (!t) return '';
  const parts = t.split(':');
  if (parts.length === 2) return `${pad2(parts[0])}:${pad2(parts[1])}:00`;
  if (parts.length === 3) return `${pad2(parts[0])}:${pad2(parts[1])}:${pad2(parts[2])}`;
  return t;
};

export const yyyyMmDd = (d) => {
  const y = d.getUTCFullYear();
  const m = pad2(d.getUTCMonth() + 1);
  const dd = pad2(d.getUTCDate());
  return `${y}-${m}-${dd}`;
};

export const computeGeneralPeriod = (periodKey, monthIndex, year) => {
  const startOfMonth = new Date(Date.UTC(year, monthIndex, 1));
  const endOfMonth = new Date(Date.UTC(year, monthIndex + 1, 0));
  const daysInMonth = endOfMonth.getUTCDate();

  const w1s = new Date(Date.UTC(year, monthIndex, 1));
  const w1e = new Date(Date.UTC(year, monthIndex, Math.min(7, daysInMonth)));
  const w2s = new Date(Date.UTC(year, monthIndex, 8));
  const w2e = new Date(Date.UTC(year, monthIndex, Math.min(14, daysInMonth)));
  const w3s = new Date(Date.UTC(year, monthIndex, 15));
  const w3e = new Date(Date.UTC(year, monthIndex, Math.min(21, daysInMonth)));
  const lastWs = new Date(Date.UTC(year, monthIndex, Math.max(22, daysInMonth - 6)));
  const lastWe = endOfMonth;

  switch (periodKey) {
    case 'first_week': return { start: yyyyMmDd(w1s), end: yyyyMmDd(w1e) };
    case 'second_week': return { start: yyyyMmDd(w2s), end: yyyyMmDd(w2e) };
    case 'third_week': return { start: yyyyMmDd(w3s), end: yyyyMmDd(w3e) };
    case 'last_week': return { start: yyyyMmDd(lastWs), end: yyyyMmDd(lastWe) };
    case 'first_2_weeks': return { start: yyyyMmDd(w1s), end: yyyyMmDd(w2e) };
    case 'last_2_weeks': {
      const s = new Date(Date.UTC(year, monthIndex, Math.max(8, daysInMonth - 13)));
      return { start: yyyyMmDd(s), end: yyyyMmDd(lastWe) };
    }
    case 'full_month': return { start: yyyyMmDd(startOfMonth), end: yyyyMmDd(endOfMonth) };
    default: return { start: yyyyMmDd(startOfMonth), end: yyyyMmDd(endOfMonth) };
  }
};
