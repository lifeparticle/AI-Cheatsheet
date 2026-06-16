import raw from '../../../marketing-data/data.json'

export type MarketingCategory =
  | 'platform_change'
  | 'competitor_campaign'
  | 'consumer_trend'
  | 'regulation'

export type MarketingItem = {
  event: string
  category: MarketingCategory
  description: string
  analyst_take: string
  brand_take: string
  recommended_actions: string[]
  source: string
  date: string
}

export type MarketingData = Record<string, MarketingItem[]>

// Local fallback data (and default when `VITE_MARKETING_URL` is missing).
export const defaultMarketingData = raw as MarketingData

function isMarketingData(value: unknown): value is MarketingData {
  if (!value || typeof value !== 'object') return false
  const rec = value as Record<string, unknown>

  const isItem = (item: unknown): item is MarketingItem => {
    if (!item || typeof item !== 'object') return false
    const it = item as Record<string, unknown>
    return (
      typeof it.event === 'string' &&
      typeof it.category === 'string' &&
      typeof it.description === 'string' &&
      typeof it.analyst_take === 'string' &&
      typeof it.brand_take === 'string' &&
      Array.isArray(it.recommended_actions) &&
      it.recommended_actions.every((a) => typeof a === 'string') &&
      typeof it.source === 'string' &&
      typeof it.date === 'string'
    )
  }

  return Object.values(rec).every((v) => Array.isArray(v) && v.every(isItem))
}

export async function fetchMarketingData(url?: string): Promise<MarketingData> {
  // If no URL is configured, use bundled marketing data.
  if (!url) return defaultMarketingData

  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(
      `Failed to fetch marketing data (${res.status} ${res.statusText})`,
    )
  }

  const json: unknown = await res.json()
  if (!isMarketingData(json)) {
    throw new Error('Marketing data was not an object')
  }

  return json
}

function sortYear(key: string, items: MarketingItem[]): number {
  const fromKey = Number.parseInt(key, 10)
  if (!Number.isNaN(fromKey)) return fromKey
  const fromDate = Number.parseInt(items[0]?.date ?? '', 10)
  return Number.isNaN(fromDate) ? 0 : fromDate
}

function sortDate(date: string): number {
  // Supports YYYY, YYYY-MM, YYYY-MM-DD. Non-matching dates go last.
  const m = /^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$/.exec(date)
  if (!m) return Number.POSITIVE_INFINITY
  const y = Number.parseInt(m[1] ?? '', 10)
  const mo = Number.parseInt(m[2] ?? '01', 10)
  const d = Number.parseInt(m[3] ?? '01', 10)
  if ([y, mo, d].some(Number.isNaN)) return Number.POSITIVE_INFINITY
  return y * 10000 + mo * 100 + d
}

/** Newest → oldest (most recent item at top). */
export function sortedMarketingEntries(
  data: MarketingData = defaultMarketingData,
): [string, MarketingItem][] {
  const flattened: [string, MarketingItem][] = []
  const years = Object.entries(data).sort(
    ([keyA, a], [keyB, b]) => sortYear(keyA, a) - sortYear(keyB, b),
  )
  for (const [year, items] of years) {
    const sortedItems = [...items].sort((a, b) => sortDate(a.date) - sortDate(b.date))
    for (const item of sortedItems) flattened.push([year, item])
  }
  return flattened.toReversed()
}

