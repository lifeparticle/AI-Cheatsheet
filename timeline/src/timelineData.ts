import raw from '../../timeline-data/data.json'

export type TimelineItem = {
  event: string
  description: string
  source: string
  date: string
}

export type TimelineData = Record<string, TimelineItem>

// Local fallback data (and default when `VITE_TIMELINE_URL` is missing).
export const defaultTimelineData = raw as TimelineData

function sortYear(key: string, item: TimelineItem): number {
  const fromDate = Number.parseInt(item.date, 10)
  if (!Number.isNaN(fromDate)) return fromDate
  const fromKey = Number.parseInt(key, 10)
  return Number.isNaN(fromKey) ? 0 : fromKey
}

function isTimelineData(value: unknown): value is TimelineData {
  return !!value && typeof value === 'object'
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
  return Object.entries(timeline).sort(
    ([keyA, a], [keyB, b]) => sortYear(keyA, a) - sortYear(keyB, b),
  )
}

/** Newest → oldest (most recent row at top). */
export function sortedTimelineEntries(
  timeline: TimelineData = defaultTimelineData,
): [string, TimelineItem][] {
  return Object.entries(timeline).sort(
    ([keyA, a], [keyB, b]) => sortYear(keyB, b) - sortYear(keyA, a),
  )
}
