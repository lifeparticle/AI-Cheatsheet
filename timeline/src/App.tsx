import {
	chronologicalTimelineEntries,
	defaultTimelineData,
	fetchTimelineData,
	sortedTimelineEntries,
	timelineEntryId,
	type TimelineItem,
} from "./timelineData";
import { useQuery } from "@tanstack/react-query";

const TAGS = ["Core.Foundation", "Term.Definition"] as const;
const LINK_LABELS = ["Retrieve_MS", "Access_Archive"] as const;
const LINK_ICONS = ["arrow_outward", "terminal"] as const;

function getMonthName(dateStr: string): string | null {
	// Supports:
	// - YYYY-MM-DD
	// - YYYY-MM
	// - anything else (e.g. just YYYY) returns null
	const re = /^(\d{4})-(\d{2})(?:-\d{2})?$/;
	const match = re.exec(dateStr);
	if (!match) return null;

	const monthIndex = Number.parseInt(match[2] ?? "", 10) - 1;
	if (Number.isNaN(monthIndex) || monthIndex < 0 || monthIndex > 11)
		return null;

	const months = [
		"January",
		"February",
		"March",
		"April",
		"May",
		"June",
		"July",
		"August",
		"September",
		"October",
		"November",
		"December",
	] as const;

	return months[monthIndex] ?? null;
}

function TimelineRow({
	year,
	item,
	chronologicalIndex,
}: Readonly<{
	year: string;
	item: TimelineItem;
	chronologicalIndex: number;
}>) {
	const monthName = getMonthName(item.date);
	const isPrimarySide = chronologicalIndex % 2 === 0;
	const tag = TAGS[chronologicalIndex % TAGS.length];
	const linkLabel = LINK_LABELS[chronologicalIndex % LINK_LABELS.length];
	const linkIcon = LINK_ICONS[chronologicalIndex % LINK_ICONS.length];

	const dotShadow = isPrimarySide
		? "shadow-[0_0_20px_rgba(143,245,255,1)]"
		: "shadow-[0_0_20px_rgba(255,89,227,1)]";
	const dotBg = isPrimarySide ? "bg-primary" : "bg-tertiary";
	const borderAccent = isPrimarySide
		? "border-primary/20"
		: "border-tertiary/20";
	const tagText = isPrimarySide ? "text-primary-fixed" : "text-tertiary-fixed";
	const yearTint = isPrimarySide ? "text-primary/40" : "text-tertiary/40";
	const titleHover = isPrimarySide
		? "group-hover:text-primary"
		: "group-hover:text-tertiary";
	const linkColor = isPrimarySide ? "text-primary" : "text-tertiary";
	const linkBorder = isPrimarySide
		? "border-primary/20 group-hover/link:border-primary"
		: "border-tertiary/20 group-hover/link:border-tertiary";

	const rowLayout = isPrimarySide
		? "flex-col md:flex-row"
		: "flex-col md:flex-row-reverse";
	const metaPadding = isPrimarySide
		? "md:pr-12 lg:pr-14 md:text-right md:justify-end"
		: "md:pl-12 lg:pl-14";
	const bodyPadding = isPrimarySide
		? "md:pl-12 lg:pl-14"
		: "md:pr-12 lg:pr-14 md:text-right md:pl-0";
	const yearMargin = isPrimarySide ? "md:mr-0 mr-4" : "mr-4 md:mr-0 md:ml-4";
	/** Mobile: padding (not margin) so w-full children stay within the viewport */
	const mobileSpineGutter = "pl-[3.75rem] md:pl-0";
	const linkJustify = isPrimarySide ? "" : "md:justify-end";

	return (
		<div
			className={`mb-10 md:mb-28 lg:mb-32 relative flex ${rowLayout} items-start gap-3 md:gap-0 ${mobileSpineGutter} min-w-0`}
		>
			<div
				className={`absolute left-4 z-20 -translate-x-1/2 md:left-1/2 md:-translate-x-1/2 w-2 h-2 ${dotBg} rounded-full ${dotShadow} top-2 ring-[3px] ring-surface`}
			/>
			<div
				className={`w-full min-w-0 md:w-1/2 flex items-start pt-1 ${metaPadding}`}
			>
				<div
					className={`vertical-year font-body text-base md:text-2xl lg:text-3xl font-bold ${yearTint} tracking-[0.2em] ${yearMargin}`}
				>
					{year}
				</div>
				<div className="hidden md:block">
					<span
						className={`inline-block py-1 px-3 border ${borderAccent} ${tagText} text-[10px] font-body uppercase tracking-widest mb-4`}
					>
						{tag}
					</span>
				</div>
			</div>
			<div className={`w-full min-w-0 md:w-1/2 ${bodyPadding}`}>
				<div className="group min-w-0">
					<h2
						className={`text-lg md:text-xl lg:text-2xl font-headline font-bold text-on-surface mb-4 md:mb-5 ${titleHover} transition-colors leading-snug md:leading-snug tracking-tight uppercase break-words [overflow-wrap:anywhere]`}
					>
						{item.event}
					</h2>
					{monthName ? (
						<p className="text-on-surface-variant font-body text-[10px] uppercase tracking-widest opacity-70 mb-4 md:mb-5">
							{monthName}
						</p>
					) : null}
					<p
						className={`text-on-surface-variant font-body text-[11px] md:text-xs lg:text-[13px] leading-loose md:leading-loose lg:leading-[1.75] mb-6 md:mb-7 projected-text max-w-full md:max-w-lg break-words [overflow-wrap:anywhere] ${isPrimarySide ? "" : "md:ml-auto"}`}
					>
						{item.description}
					</p>
					<div
						className={`flex items-center space-x-6 mt-2 pt-4 md:mt-0 md:pt-6 ${linkJustify}`}
					>
						<a
							className={`${linkColor} text-[10px] font-body font-bold uppercase tracking-[0.2em] flex items-center group/link`}
							href={item.source}
							target="_blank"
							rel="noopener noreferrer"
						>
							<span className={`border-b ${linkBorder} transition-all`}>
								{linkLabel}
							</span>
							<span
								className={`material-symbols-outlined text-xs ml-2 opacity-50`}
							>
								{linkIcon}
							</span>
						</a>
					</div>
				</div>
			</div>
		</div>
	);
}

export default function App() {
	const {
		data: timeline,
		isLoading,
		isError,
		error,
	} = useQuery({
		queryKey: ["timeline-data", import.meta.env.VITE_TIMELINE_URL ?? ""],
		queryFn: () => fetchTimelineData(import.meta.env.VITE_TIMELINE_URL),
	});

	const timelineForUI = timeline ?? defaultTimelineData;

	const entries = sortedTimelineEntries(timelineForUI);
	const chronIndexById = new Map(
		chronologicalTimelineEntries(timelineForUI).map(([y, item], i) => [
			timelineEntryId(y, item),
			i,
		]),
	);
	const years = entries.map(([y]) => Number(y));
	const span =
		years.length >= 2
			? `${Math.min(...years)}–${Math.max(...years)}`
			: (years[0]?.toString() ?? "—");

	return (
		<>
			<main className="pt-16 md:pt-24 lg:pt-28 pb-32 md:pb-44 lg:pb-52 min-h-screen relative bg-surface text-on-surface selection:bg-primary/30 overflow-x-hidden">
				<div
					className="fixed inset-0 digital-grid pointer-events-none"
					aria-hidden
				/>
				<div
					className="fixed inset-0 scanner-line pointer-events-none"
					aria-hidden
				/>
				<div
					className="fixed top-0 right-0 w-[800px] h-[800px] bg-primary/5 blur-[160px] rounded-full pointer-events-none"
					aria-hidden
				/>
				<div
					className="fixed bottom-0 left-0 w-[600px] h-[600px] bg-tertiary/5 blur-[140px] rounded-full pointer-events-none"
					aria-hidden
				/>

				<div className="max-w-5xl mx-auto w-full min-w-0 px-6 md:px-8 lg:px-10 relative z-10">
					<header className="mb-16 md:mb-28 lg:mb-32 text-center flex flex-col items-center">
						<span className="text-tertiary font-body text-xs font-bold tracking-[0.5em] uppercase mb-6 md:mb-6 opacity-60">
							System.Genesis_Logs
						</span>
						<h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-headline font-bold text-on-surface tracking-tight md:tracking-tighter leading-tight mb-5 md:mb-6">
							THE AI
							<br />
							<span className="text-primary-dim">EVOLUTION</span>
						</h1>
						<p className="max-w-xl md:max-w-2xl text-on-surface-variant text-sm md:text-sm leading-loose md:leading-relaxed font-body uppercase tracking-widest md:tracking-[0.35em] opacity-80 projected-text">
							Mapping the transition from theoretical computation to autonomous
							neural synthesis.
						</p>
					</header>

					<div className="relative">
						<div className="absolute left-4 top-0 bottom-0 w-px -translate-x-1/2 bg-gradient-to-b from-primary via-primary/20 to-transparent md:left-1/2 md:-translate-x-1/2 central-line-glow" />

						{isLoading ? (
							<p className="text-center text-on-surface-variant/70 font-body text-xs uppercase tracking-[0.35em] mb-8">
								Syncing timeline...
							</p>
						) : null}

						{isError ? (
							<p className="text-center text-tertiary font-body text-xs uppercase tracking-[0.35em] mb-8">
								Failed to load remote timeline.{" "}
								{error instanceof Error ? error.message : "Showing local data."}
							</p>
						) : null}

						{entries.map(([year, item]) => (
							<TimelineRow
								key={timelineEntryId(year, item)}
								year={year}
								item={item}
								chronologicalIndex={
									chronIndexById.get(timelineEntryId(year, item)) ?? 0
								}
							/>
						))}

						<div className="mb-32 md:mb-40 mx-auto max-w-xl">
							<div className="relative py-12 md:py-14 px-8 md:px-10">
								<div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-primary/30" />
								<div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-primary/30" />
								<div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-primary/30" />
								<div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-primary/30" />

								<div className="text-center">
									<span className="material-symbols-outlined text-primary mb-6 text-3xl opacity-80">
										hub
									</span>
									<h3 className="text-lg font-headline font-bold text-on-surface mb-2 uppercase tracking-widest">
										Hardware_Synthesis
									</h3>
									<p className="text-on-surface-variant font-body text-[11px] uppercase tracking-widest mb-10 opacity-60">
										Neural Network Initial Benchmarks
									</p>
								</div>
								<div className="grid grid-cols-2 gap-12">
									<div className="text-center">
										<p className="text-[9px] uppercase font-body tracking-[0.3em] text-on-surface-variant/50 mb-2">
											Timeline_Span
										</p>
										<p className="text-xl font-body font-bold text-primary">
											{span}
										</p>
									</div>
									<div className="text-center">
										<p className="text-[9px] uppercase font-body tracking-[0.3em] text-on-surface-variant/50 mb-2">
											Log_Entries
										</p>
										<p className="text-xl font-body font-bold text-secondary">
											{String(entries.length).padStart(2, "0")}_Events
										</p>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</main>

			<footer className="py-12 relative z-10 bg-surface">
				<div className="max-w-5xl mx-auto px-6 flex flex-col items-center text-on-surface-variant/40 font-body text-[9px] uppercase tracking-[0.4em]">
					<div className="flex items-center space-x-2 mb-2">
						<div className="w-2 h-2 bg-primary/20 rounded-full animate-pulse" />
						<span>System_Status: Operational</span>
					</div>
					<div>AI_ARCHIVE_NODE // v1.0.2</div>
				</div>
			</footer>
		</>
	);
}
