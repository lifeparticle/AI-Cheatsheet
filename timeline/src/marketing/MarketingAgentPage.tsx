import { useQuery } from '@tanstack/react-query'
import { defaultMarketingData, fetchMarketingData, sortedMarketingEntries } from './marketingData'

function categoryLabel(category: string): string {
  switch (category) {
    case 'platform_change':
      return 'Platform / Measurement'
    case 'competitor_campaign':
      return 'Competitor / Campaign'
    case 'consumer_trend':
      return 'Consumer Trend'
    case 'regulation':
      return 'Regulation'
    default:
      return category
  }
}

export function MarketingAgentPage() {
  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['marketing-data', import.meta.env.VITE_MARKETING_URL ?? ''],
    queryFn: () => fetchMarketingData(import.meta.env.VITE_MARKETING_URL),
  })

  const marketingForUI = data ?? defaultMarketingData
  const entries = sortedMarketingEntries(marketingForUI)

  let statusNode: React.ReactNode = <span className="sr-only">Marketing data loaded.</span>
  if (isLoading) {
    statusNode = (
      <p className="text-center text-on-surface-variant/70 font-body text-xs uppercase tracking-[0.35em] inline-flex items-center bg-surface/85 backdrop-blur-sm px-4 py-1 border border-on-surface/10 shadow-[0_0_24px_rgba(0,0,0,0.25)]">
        Syncing marketing intel...
      </p>
    )
  } else if (isError) {
    const errorMessage = error instanceof Error ? error.message : 'Showing local data.'
    statusNode = (
      <p className="text-center text-tertiary font-body text-xs uppercase tracking-[0.35em] inline-flex items-center bg-surface/85 backdrop-blur-sm px-4 py-1 border border-tertiary/20 shadow-[0_0_24px_rgba(0,0,0,0.25)]">
        Failed to load remote marketing data. {errorMessage}
      </p>
    )
  }

  return (
    <main className="pt-16 pb-32 min-h-screen relative bg-surface text-on-surface selection:bg-primary/30 overflow-x-hidden">
      <div className="fixed inset-0 digital-grid pointer-events-none" aria-hidden />
      <div className="fixed inset-0 scanner-line pointer-events-none" aria-hidden />
      <div
        className="fixed top-0 right-0 w-[800px] h-[800px] bg-primary/5 blur-[160px] rounded-full pointer-events-none"
        aria-hidden
      />
      <div
        className="fixed bottom-0 left-0 w-[600px] h-[600px] bg-tertiary/5 blur-[140px] rounded-full pointer-events-none"
        aria-hidden
      />

      <div className="max-w-5xl mx-auto w-full min-w-0 px-6 md:px-8 lg:px-10 relative z-10">
        <header className="mb-12 text-center flex flex-col items-center">
          <span className="text-tertiary font-body text-xs font-bold tracking-[0.5em] uppercase mb-6 opacity-60">
            System.Genesis_Intel
          </span>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-headline font-bold text-on-surface tracking-tight leading-tight mb-5">
            MARKETING
            <br />
            <span className="text-primary-dim">INTELLIGENCE</span>
          </h1>
          <p className="max-w-2xl text-on-surface-variant text-sm leading-relaxed font-body uppercase tracking-[0.35em] opacity-80 projected-text">
            Daily signals for analysts and brand leaders.
          </p>
        </header>

        <div className="mb-8 h-6 flex items-center justify-center" aria-live="polite" aria-atomic="true">
          {statusNode}
        </div>

        <div className="grid gap-6 md:gap-8">
          {entries.map(([year, item]) => (
            <article
              key={`${year}|${item.date}|${item.event}`}
              className="relative bg-surface/70 border border-on-surface/10 shadow-[0_0_24px_rgba(0,0,0,0.25)] backdrop-blur-sm p-6 md:p-8"
            >
              <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-primary/30" />
              <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-primary/30" />
              <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-primary/30" />
              <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-primary/30" />

              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-3 mb-3">
                    <span className="inline-block py-1 px-3 border border-primary/20 text-primary-fixed text-[10px] font-body uppercase tracking-widest">
                      {categoryLabel(item.category)}
                    </span>
                    <span className="text-on-surface-variant/70 text-[10px] font-body uppercase tracking-[0.35em]">
                      {item.date}
                    </span>
                  </div>

                  <h2 className="text-lg md:text-xl font-headline font-bold text-on-surface tracking-tight uppercase break-words [overflow-wrap:anywhere]">
                    {item.event}
                  </h2>
                </div>

                <a
                  className="shrink-0 text-primary text-[10px] font-body font-bold uppercase tracking-[0.2em] flex items-center group/link"
                  href={item.source}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span className="border-b border-primary/20 group-hover/link:border-primary transition-all">
                    Retrieve_MS
                  </span>
                  <span className="material-symbols-outlined text-xs ml-2 opacity-50">arrow_outward</span>
                </a>
              </div>

              <p className="mt-5 text-on-surface-variant font-body text-[12px] leading-loose projected-text">
                {item.description}
              </p>

              <div className="mt-6 grid md:grid-cols-2 gap-6">
                <section>
                  <h3 className="text-[10px] uppercase font-body tracking-[0.35em] text-on-surface-variant/60 mb-2">
                    Analyst_take
                  </h3>
                  <p className="text-on-surface-variant font-body text-[12px] leading-loose">
                    {item.analyst_take}
                  </p>
                </section>

                <section>
                  <h3 className="text-[10px] uppercase font-body tracking-[0.35em] text-on-surface-variant/60 mb-2">
                    Brand_take
                  </h3>
                  <p className="text-on-surface-variant font-body text-[12px] leading-loose">
                    {item.brand_take}
                  </p>
                </section>
              </div>

              {item.recommended_actions?.length ? (
                <section className="mt-6">
                  <h3 className="text-[10px] uppercase font-body tracking-[0.35em] text-on-surface-variant/60 mb-2">
                    Recommended_actions
                  </h3>
                  <ul className="list-disc pl-5 space-y-1 text-on-surface-variant font-body text-[12px] leading-loose">
                    {item.recommended_actions.map((a) => (
                      <li key={a}>{a}</li>
                    ))}
                  </ul>
                </section>
              ) : null}
            </article>
          ))}
        </div>
      </div>
    </main>
  )
}

