"use client";
import type { CampaignStrategy } from "@/interfaces/campaign.type";

interface Props {
    strategy: CampaignStrategy | null;
}

export default function CampaignTab({ strategy }: Props) {
    if (!strategy) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-center text-[#A0A7A3]">
                <p className="text-sm">Strategy not generated yet.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* ── Name & Summary ───────────────────────────────── */}
            <Section title="Campaign Overview">
                <div className="space-y-3">
                    {strategy.name && (
                        <div>
                            <Label>Name</Label>
                            <p className="text-sm text-[#1E2A24] font-medium">
                                {strategy.name}
                            </p>
                        </div>
                    )}
                    {strategy.summary && (
                        <div>
                            <Label>Summary</Label>
                            <p className="text-sm text-[#4A5B50] leading-relaxed">
                                {strategy.summary}
                            </p>
                        </div>
                    )}
                    {strategy.timeline && (
                        <div className="flex gap-3">
                            <MiniCard
                                label="Duration"
                                value={`${strategy.timeline.duration_in_weeks ?? "—"} weeks`}
                            />
                            <MiniCard
                                label="Status"
                                value="Active"
                                accent
                            />
                        </div>
                    )}
                </div>
            </Section>

            {/* ── Target Audience ──────────────────────────────── */}
            {strategy.target_audience && (
                <Section title="Target Audience">
                    <div className="space-y-2">
                        <div className="flex gap-3">
                            {strategy.target_audience.age_range && (
                                <MiniCard
                                    label="Age"
                                    value={strategy.target_audience.age_range}
                                />
                            )}
                            {strategy.target_audience.gender && (
                                <MiniCard
                                    label="Gender"
                                    value={strategy.target_audience.gender}
                                />
                            )}
                            {strategy.target_audience.income && (
                                <MiniCard
                                    label="Income"
                                    value={strategy.target_audience.income}
                                />
                            )}
                        </div>
                        {strategy.target_audience.interests?.length > 0 && (
                            <div>
                                <Label>Interests</Label>
                                <TagList items={strategy.target_audience.interests} />
                            </div>
                        )}
                        {strategy.target_audience.demographics?.length > 0 && (
                            <div>
                                <Label>Demographics</Label>
                                <TagList items={strategy.target_audience.demographics} />
                            </div>
                        )}
                    </div>
                </Section>
            )}

            {/* ── Key Messages ─────────────────────────────────── */}
            {strategy.key_messages?.length > 0 && (
                <Section title="Key Messages">
                    <div className="space-y-1.5">
                        {strategy.key_messages.map((msg, i) => (
                            <div
                                key={i}
                                className="flex items-start gap-2 text-sm text-[#4A5B50]"
                            >
                                <span className="text-[#E26A4A] mt-0.5 text-xs">●</span>
                                {msg}
                            </div>
                        ))}
                    </div>
                </Section>
            )}

            {/* ── Goals & Metrics ──────────────────────────────── */}
            {strategy.goal && (
                <Section title="Goals & Metrics">
                    <div className="space-y-2">
                        {strategy.goal.goal && (
                            <div>
                                <Label>Primary Goal</Label>
                                <p className="text-sm text-[#1E2A24] font-medium">
                                    {strategy.goal.goal}
                                </p>
                            </div>
                        )}
                        {strategy.goal.success_metrics?.length > 0 && (
                            <div className="grid grid-cols-2 gap-2">
                                {strategy.goal.success_metrics.map((m, i) => (
                                    <div
                                        key={i}
                                        className="bg-[#F6F4EB] rounded-lg p-3 border border-[#EBE7DC]"
                                    >
                                        <p className="text-[10px] uppercase tracking-wider text-[#A0A7A3] font-medium">
                                            {m.metric_name}
                                        </p>
                                        <p className="text-sm font-semibold text-[#1E2A24] mt-0.5">
                                            {m.metric_value}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </Section>
            )}

            {/* ── Content Direction ────────────────────────────── */}
            {strategy.content_direction && (
                <Section title="Content Direction">
                    <div className="space-y-2">
                        <div className="flex flex-wrap gap-2">
                            {strategy.content_direction.tone && (
                                <MiniCard
                                    label="Tone"
                                    value={strategy.content_direction.tone}
                                />
                            )}
                        </div>
                        {strategy.content_direction.style &&
                            strategy.content_direction.style.length > 0 && (
                                <div>
                                    <Label>Style</Label>
                                    <TagList items={strategy.content_direction.style} />
                                </div>
                            )}
                        {strategy.content_direction.visual_theme &&
                            strategy.content_direction.visual_theme.length > 0 && (
                                <div>
                                    <Label>Visual Theme</Label>
                                    <TagList items={strategy.content_direction.visual_theme} />
                                </div>
                            )}

                        {/* Posting Schedule */}
                        {strategy.content_direction.posting_strategy && (
                            <div className="mt-2 bg-[#F6F4EB] rounded-lg p-3 border border-[#EBE7DC]">
                                <p className="text-[10px] uppercase tracking-wider text-[#A0A7A3] font-medium mb-2">
                                    Posting Schedule
                                </p>
                                <div className="space-y-1.5 text-sm text-[#4A5B50]">
                                    <p>
                                        <span className="text-[#1E2A24] font-medium">
                                            {strategy.content_direction.posting_strategy.frequency_per_week}×
                                        </span>{" "}
                                        per week
                                    </p>
                                    {strategy.content_direction.posting_strategy.posting_days?.length > 0 && (
                                        <p>
                                            {strategy.content_direction.posting_strategy.posting_days.join(", ")}
                                        </p>
                                    )}
                                    {strategy.content_direction.posting_strategy.posting_hours?.length > 0 && (
                                        <p className="text-xs text-[#A0A7A3]">
                                            at{" "}
                                            {strategy.content_direction.posting_strategy.posting_hours.join(
                                                " & "
                                            )}
                                        </p>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </Section>
            )}
        </div>
    );
}

/* ── Shared sub-components ───────────────────────────────────────────────── */

function Section({
    title,
    children,
}: {
    title: string;
    children: React.ReactNode;
}) {
    return (
        <div className="bg-white border border-[#EBE7DC] rounded-xl p-4 shadow-sm">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[#A0A7A3] mb-3">
                {title}
            </h3>
            {children}
        </div>
    );
}

function Label({ children }: { children: React.ReactNode }) {
    return (
        <p className="text-[10px] uppercase tracking-wider text-[#A0A7A3] font-medium mb-1">
            {children}
        </p>
    );
}

function TagList({ items }: { items: string[] }) {
    return (
        <div className="flex flex-wrap gap-1.5">
            {items.map((item, i) => (
                <span
                    key={i}
                    className="inline-block px-2.5 py-1 text-xs font-medium bg-[#F6F4EB] text-[#4A5B50] rounded-full border border-[#EBE7DC]"
                >
                    {item}
                </span>
            ))}
        </div>
    );
}

function MiniCard({
    label,
    value,
    accent,
}: {
    label: string;
    value: string;
    accent?: boolean;
}) {
    return (
        <div className="flex-1 bg-[#F6F4EB] rounded-lg p-2.5 border border-[#EBE7DC] min-w-0">
            <p className="text-[10px] uppercase tracking-wider text-[#A0A7A3] font-medium">
                {label}
            </p>
            <p
                className={`text-sm font-semibold mt-0.5 truncate ${
                    accent ? "text-emerald-600" : "text-[#1E2A24]"
                }`}
            >
                {value}
            </p>
        </div>
    );
}
