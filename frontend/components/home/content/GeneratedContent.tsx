"use client";
import { useState } from "react";
import { useCampaign } from "@/lib/campaign-context";
import CampaignTab from "./tabs/CampaignTab";
import PostsTab from "./tabs/PostsTab";
import MediaTab from "./tabs/MediaTab";

const TABS = [
    { id: "campaign", label: "Campaign" },
    { id: "posts", label: "Posts" },
    { id: "media", label: "Media" },
] as const;

type TabId = (typeof TABS)[number]["id"];


export default function GeneratedContent() {
    const [activeTab, setActiveTab] = useState<TabId>("campaign");
    const { campaign, loading } = useCampaign();

    return (
        <div className="w-[380px] lg:w-[450px] xl:w-[500px] h-full bg-white border-l border-[#EBE7DC] flex-col hidden md:flex">
            {/* ── Header ───────────────────────────────────────── */}
            <header className="h-16 flex items-center justify-between px-6 border-b border-[#EBE7DC]">
                <h2 className="font-medium text-[#1E2A24]">
                    Generated Content
                </h2>
                {campaign && (
                    <span
                        className={`px-2.5 py-1 text-xs font-medium rounded-full ${campaign.status === "completed"
                                ? "bg-emerald-50 text-emerald-600"
                                : campaign.status === "generating"
                                    ? "bg-amber-50 text-amber-600"
                                    : campaign.status === "failed"
                                        ? "bg-red-50 text-red-600"
                                        : "bg-gray-50 text-gray-500"
                            }`}
                    >
                        {campaign.status.charAt(0).toUpperCase() +
                            campaign.status.slice(1)}
                    </span>
                )}
            </header>

            {/* ── Tab bar ──────────────────────────────────────── */}
            <div className="flex border-b border-[#EBE7DC] px-4 pt-2">
                {TABS.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === tab.id
                                ? "border-[#E26A4A] text-[#1E2A24]"
                                : "border-transparent text-[#6B726F] hover:text-[#1E2A24]"
                            }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* ── Tab content ──────────────────────────────────── */}
            <div className="flex-1 overflow-y-auto p-5 bg-[#FCFBF8]">
                {loading ? (
                    <div className="flex flex-col items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#E26A4A]" />
                        <p className="text-sm text-[#A0A7A3] mt-3">Loading campaign...</p>
                    </div>
                ) : !campaign ? (
                    <EmptyState />
                ) : (
                    <>
                        {activeTab === "campaign" && (
                            <CampaignTab strategy={campaign.strategy ?? null} />
                        )}
                        {activeTab === "posts" && (
                            <PostsTab content={campaign.content ?? []} />
                        )}
                        {activeTab === "media" && (
                            <MediaTab content={campaign.content ?? []} />
                        )}
                    </>
                )}
            </div>
        </div>
    );
}

function EmptyState() {
    return (
        <div className="flex flex-col items-center justify-center h-full text-center text-[#A0A7A3]">
            <svg
                className="mb-3 opacity-40"
                width="40"
                height="40"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
            >
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
            </svg>
            <p className="text-sm font-medium">No campaign yet</p>
            <p className="text-xs mt-1">
                Start chatting to generate a campaign.
            </p>
        </div>
    );
}
