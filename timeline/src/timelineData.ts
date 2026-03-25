import raw from '../../timeline-data/data.json'

export type TimelineItem = {
  event: string
  description: string
  source: string
  date: string
}

export type TimelineData = Record<string, TimelineItem[]>

// Local fallback data (and default when `VITE_TIMELINE_URL` is missing).
export const defaultTimelineData = raw as TimelineData

export function timelineEntryId(year: string, item: TimelineItem): string {
  // Stable-enough identifier for React keys & index mapping.
  return `${year}|${item.date}|${item.event}`
}

function sortYear(key: string, items: TimelineItem[]): number {
  const fromKey = Number.parseInt(key, 10)
  if (!Number.isNaN(fromKey)) return fromKey
  const fromDate = Number.parseInt(items[0]?.date ?? '', 10)
  return Number.isNaN(fromDate) ? 0 : fromDate
}

function sortDateWithinYear(date: string): number {
  // Supports YYYY, YYYY-MM, YYYY-MM-DD. Non-matching dates go last.
  const m = /^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$/.exec(date)
  if (!m) return Number.POSITIVE_INFINITY
  const y = Number.parseInt(m[1] ?? '', 10)
  const mo = Number.parseInt(m[2] ?? '01', 10)
  const d = Number.parseInt(m[3] ?? '01', 10)
  if ([y, mo, d].some(Number.isNaN)) return Number.POSITIVE_INFINITY
  return y * 10000 + mo * 100 + d
}

function isTimelineData(value: unknown): value is TimelineData {
  if (!value || typeof value !== 'object') return false
  const rec = value as Record<string, unknown>

  const isTimelineItem = (item: unknown): item is TimelineItem => {
    if (!item || typeof item !== 'object') return false
    if (!('event' in item)) return false
    if (!('description' in item)) return false
    if (!('source' in item)) return false
    if (!('date' in item)) return false
    return (
      typeof (item as { event: unknown }).event === 'string' &&
      typeof (item as { description: unknown }).description === 'string' &&
      typeof (item as { source: unknown }).source === 'string' &&
      typeof (item as { date: unknown }).date === 'string'
    )
  }

  return Object.values(rec).every((v) => {
    if (!Array.isArray(v)) return false
    return v.every(isTimelineItem)
  })
}

export async function fetchTimelineData(
  url?: string,
): Promise<TimelineData> {
  // If no URL is configured, use bundled timeline data.
  if (!url) return defaultTimelineData

  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(
      `Failed to fetch timeline data (${res.status} ${res.statusText})`,
    )
  }

  const json: unknown = await res.json()
  if (!isTimelineData(json)) {
    throw new Error('Timeline data was not an object')
  }

  return json
}

/** Oldest → newest (for tags, colors, and alternating layout tied to era order). */
export function chronologicalTimelineEntries(
  timeline: TimelineData = defaultTimelineData,
): [string, TimelineItem][] {
  const flattened: [string, TimelineItem][] = []
  const years = Object.entries(timeline).sort(
    ([keyA, a], [keyB, b]) => sortYear(keyA, a) - sortYear(keyB, b),
  )
  for (const [year, items] of years) {
    const sortedItems = [...items].sort(
      (a, b) => sortDateWithinYear(a.date) - sortDateWithinYear(b.date),
    )
    for (const item of sortedItems) flattened.push([year, item])
  }
  return flattened
}

/** Newest → oldest (most recent row at top). */
export function sortedTimelineEntries(
  timeline: TimelineData = defaultTimelineData,
): [string, TimelineItem][] {
  return chronologicalTimelineEntries(timeline).toReversed()
}
