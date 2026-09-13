const ORDINAL_SUFFIXES = ['th', 'st', 'nd', 'rd'];

export function ordinal(n) {
  const lastTwo = n % 100;
  return n + (ORDINAL_SUFFIXES[(lastTwo - 20) % 10] || ORDINAL_SUFFIXES[lastTwo] || ORDINAL_SUFFIXES[0]);
}

export function formatGoalDifference(goalDifference) {
  if (goalDifference > 0) return `+${goalDifference}`;
  if (goalDifference < 0) return `−${Math.abs(goalDifference)}`;
  return '0';
}

export function plural(count, word) {
  return `${count} ${word}${count === 1 ? '' : 's'}`;
}

const matchDateFormat = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
});

export function formatMatchDate(isoDate) {
  return matchDateFormat.format(new Date(`${isoDate}T00:00:00Z`));
}
