"use client";
import { useState } from "react";
import type { PlatformContent } from "@/interfaces/campaign.type";

interface Props {
    content: PlatformContent[];
}

const PLATFORM_ICONS: Record<string, string> = {
    twitter: "𝕏",
    linkedin: "in",
    instagram: "📷",
};

const PLATFORM_COLORS: Record<string, string> = {
    twitter: "bg-black text-white",
    linkedin: "bg-[#0A66C2] text-white",
    instagram: "bg-gradient-to-br from-purple-500 to-pink-500 text-white",
};

export default function PostsTab({ content }: Props) {
    const platforms = content.map((c) => c.platform);
    const [activePlatform, setActivePlatform] = useState<string>(
        platforms[0] ?? ""
    );

    if (content.length === 0) {
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
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <p className="text-sm">No posts generated yet.</p>
                <p className="text-xs mt-1">
                    Ask the AI to create content for your campaign.
                </p>
            </div>
        );
    }

    const activePlatformContent = content.find(
        (c) => c.platform === activePlatform
    );
    const posts = activePlatformContent?.posts?.posts ?? [];

    return (
        <div className="space-y-4">
            {/* ── Platform pills ────────────────────────────────── */}
            <div className="flex gap-2">
                {platforms.map((platform) => (
                    <button
                        key={platform}
                        onClick={() => setActivePlatform(platform)}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                            activePlatform === platform
                                ? `${PLATFORM_COLORS[platform] ?? "bg-[#1E2A24] text-white"} shadow-sm`
                                : "bg-white text-[#6B726F] border border-[#EBE7DC] hover:border-[#C4C0B4]"
                        }`}
                    >
                        <span className="text-sm leading-none">
                            {PLATFORM_ICONS[platform] ?? "●"}
                        </span>
                        {platform.charAt(0).toUpperCase() + platform.slice(1)}
                    </button>
                ))}
            </div>

            {/* ── Post cards ───────────────────────────────────── */}
            {posts.length === 0 ? (
                <div className="text-center text-sm text-[#A0A7A3] py-8">
                    No posts for this platform yet.
                </div>
            ) : (
                <div className="space-y-3">
                    {posts.map((post, i) => (
                        <div
                            key={i}
                            className="bg-white border border-[#EBE7DC] rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
                        >
                            {/* Post header */}
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <span
                                        className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
                                            PLATFORM_COLORS[post.platform] ??
                                            "bg-gray-200 text-gray-600"
                                        }`}
                                    >
                                        {PLATFORM_ICONS[post.platform] ?? "●"}
                                    </span>
                                    <span className="text-sm font-medium text-[#1E2A24]">
                                        {post.name}
                                    </span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    {post.has_media && (
                                        <span className="flex items-center gap-1 text-[10px] font-medium text-[#E26A4A] bg-[#F8E5DB] px-2 py-0.5 rounded-full">
                                            <svg
                                                width="10"
                                                height="10"
                                                viewBox="0 0 24 24"
                                                fill="none"
                                                stroke="currentColor"
                                                strokeWidth="2.5"
                                            >
                                                <rect
                                                    x="3"
                                                    y="3"
                                                    width="18"
                                                    height="18"
                                                    rx="2"
                                                    ry="2"
                                                />
                                                <circle cx="8.5" cy="8.5" r="1.5" />
                                                <polyline points="21 15 16 10 5 21" />
                                            </svg>
                                            Media
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Post text */}
                            <p className="text-sm text-[#4A5B50] leading-relaxed whitespace-pre-wrap">
                                {post.post_text}
                            </p>

                            {/* Post footer */}
                            <div className="flex items-center justify-between mt-3 pt-3 border-t border-[#EBE7DC]">
                                <span className="text-[10px] uppercase tracking-wider text-[#A0A7A3] font-medium">
                                    {post.platform}
                                </span>
                                <button className="text-xs text-[#6B726F] hover:text-[#1E2A24] transition-colors flex items-center gap-1">
                                    <svg
                                        width="12"
                                        height="12"
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        stroke="currentColor"
                                        strokeWidth="2"
                                    >
                                        <rect
                                            x="9"
                                            y="9"
                                            width="13"
                                            height="13"
                                            rx="2"
                                            ry="2"
                                        />
                                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                                    </svg>
                                    Copy
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
