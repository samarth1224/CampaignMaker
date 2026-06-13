"use client";
import { useState, useMemo } from "react";
import type { PlatformContent, PostContent } from "@/interfaces/campaign.type";

interface Props {
    content: PlatformContent[];
}

const PLATFORM_COLORS: Record<string, string> = {
    twitter: "bg-black text-white",
    linkedin: "bg-[#0A66C2] text-white",
    instagram: "bg-gradient-to-br from-purple-500 to-pink-500 text-white",
};

export default function MediaTab({ content }: Props) {
    const platforms = content.map((c) => c.platform);
    const [filter, setFilter] = useState<string>("all");

    // Flatten all media with platform labels
    const allMedia = useMemo(() => {
        const items: { platform: string; media: PostContent }[] = [];
        for (const platformContent of content) {
            for (const media of platformContent.media) {
                items.push({ platform: platformContent.platform, media });
            }
        }
        return items;
    }, [content]);

    const filteredMedia =
        filter === "all"
            ? allMedia
            : allMedia.filter((m) => m.platform === filter);

    if (allMedia.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-center text-[#A0A7A3]">
                <svg
                    className="mb-3 opacity-40"
                    width="32"
                    height="32"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.5"
                >
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                </svg>
                <p className="text-sm">No media generated yet.</p>
                <p className="text-xs mt-1">
                    Media will appear here once posts with illustrations are
                    created.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* ── Filter bar ───────────────────────────────────── */}
            <div className="flex gap-2 flex-wrap">
                <FilterPill
                    label="All Media"
                    count={allMedia.length}
                    active={filter === "all"}
                    onClick={() => setFilter("all")}
                />
                {platforms.map((platform) => {
                    const count = allMedia.filter(
                        (m) => m.platform === platform
                    ).length;
                    if (count === 0) return null;
                    return (
                        <FilterPill
                            key={platform}
                            label={
                                platform.charAt(0).toUpperCase() +
                                platform.slice(1)
                            }
                            count={count}
                            active={filter === platform}
                            onClick={() => setFilter(platform)}
                        />
                    );
                })}
            </div>

            {/* ── Media grid ───────────────────────────────────── */}
            <div className="grid grid-cols-2 gap-3">
                {filteredMedia.map(({ platform, media }, i) => (
                    <div
                        key={i}
                        className="bg-white border border-[#EBE7DC] rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow group"
                    >
                        {/* SVG preview */}
                        <div className="aspect-square bg-[#F6F4EB] flex items-center justify-center p-4 relative">
                            <div
                                className="w-full h-full [&>svg]:w-full [&>svg]:h-full"
                                dangerouslySetInnerHTML={{
                                    __html: media.svg_code,
                                }}
                            />
                            {/* Platform badge */}
                            <span
                                className={`absolute top-2 left-2 w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-bold ${
                                    PLATFORM_COLORS[platform] ??
                                    "bg-gray-200 text-gray-600"
                                }`}
                            >
                                {platform.charAt(0).toUpperCase()}
                            </span>
                            {/* Hover overlay */}
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors" />
                        </div>

                        {/* Media info */}
                        <div className="p-3 flex items-center justify-between">
                            <div className="min-w-0">
                                <p className="text-xs font-medium text-[#1E2A24] truncate">
                                    {media.media_name}
                                </p>
                                <p className="text-[10px] text-[#A0A7A3] uppercase tracking-wider">
                                    SVG · {platform}
                                </p>
                            </div>
                            <button
                                className="text-[#6B726F] hover:text-[#1E2A24] transition-colors p-1 flex-shrink-0"
                                title="Download SVG"
                                onClick={() => {
                                    const blob = new Blob(
                                        [media.svg_code],
                                        { type: "image/svg+xml" }
                                    );
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement("a");
                                    a.href = url;
                                    a.download = `${media.media_name}.svg`;
                                    a.click();
                                    URL.revokeObjectURL(url);
                                }}
                            >
                                <svg
                                    width="14"
                                    height="14"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                >
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                    <polyline points="7 10 12 15 17 10" />
                                    <line x1="12" y1="15" x2="12" y2="3" />
                                </svg>
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function FilterPill({
    label,
    count,
    active,
    onClick,
}: {
    label: string;
    count: number;
    active: boolean;
    onClick: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                active
                    ? "bg-[#1E2A24] text-white shadow-sm"
                    : "bg-white text-[#6B726F] border border-[#EBE7DC] hover:border-[#C4C0B4]"
            }`}
        >
            {label}
            <span
                className={`inline-flex items-center justify-center w-4 h-4 rounded-full text-[10px] font-bold ${
                    active
                        ? "bg-white/20 text-white"
                        : "bg-[#F6F4EB] text-[#A0A7A3]"
                }`}
            >
                {count}
            </span>
        </button>
    );
}
