"use client";
import { useState, useEffect } from "react";
import { useCampaign, CampaignListItem } from "@/lib/campaign-context";
import { useAuth } from "@/lib/auth-context";

export default function Sidebar() {
    const [isOpen, setIsOpen] = useState(true);
    const { user } = useAuth();
    const {
        campaignList,
        campaignId: activeCampaignId,
        fetchCampaignList,
        fetchCampaign,
        setCampaignId,
        setCampaign,
    } = useCampaign();

    // Fetch campaign list on mount
    useEffect(() => {
        fetchCampaignList();
    }, [fetchCampaignList]);

    const handleNewCampaign = () => {
        setCampaignId(null);
        setCampaign(null);
    };

    const handleSelectCampaign = (id: string) => {
        fetchCampaign(id);
    };

    const formatDate = (dateStr: string) => {
        const d = new Date(dateStr);
        const now = new Date();
        const diffMs = now.getTime() - d.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return "Just now";
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    };

    const statusDot: Record<string, string> = {
        completed: "bg-emerald-500",
        generating: "bg-amber-500 animate-pulse",
        failed: "bg-red-500",
        draft: "bg-gray-400",
    };

    return (
        <aside className={`h-screen bg-white border-r border-[#EBE7DC] transition-all duration-300 flex flex-col ${isOpen ? "w-64" : "w-16"}`}>
            {/* ── Header ────────────────────────────────────────── */}
            <div className="h-16 flex items-center justify-between px-4 border-b border-[#EBE7DC]">
                {isOpen && (
                    <span className="font-serif text-lg font-semibold text-[#1E2A24] truncate">
                        CampaignMaker <span className="text-[#E26A4A] italic">AI</span>
                    </span>
                )}
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="p-1.5 rounded-lg hover:bg-[#F6F4EB] text-[#6B726F] transition-colors flex-shrink-0 mx-auto"
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="3" y1="12" x2="21" y2="12"></line>
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <line x1="3" y1="18" x2="21" y2="18"></line>
                    </svg>
                </button>
            </div>

            {/* ── New Campaign button ───────────────────────────── */}
            <div className="px-2 pt-4 pb-2">
                <button
                    onClick={handleNewCampaign}
                    className={`w-full flex items-center gap-3 p-3 rounded-xl text-[#1E2A24] hover:bg-[#F6F4EB] transition-colors ${!isOpen && "justify-center"}`}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0">
                        <path d="M12 5v14M5 12h14" />
                    </svg>
                    {isOpen && <span className="font-medium text-sm whitespace-nowrap">New Campaign</span>}
                </button>
            </div>

            {/* ── Campaign list ─────────────────────────────────── */}
            <nav className="flex-1 overflow-y-auto px-2 space-y-0.5">
                {isOpen && campaignList.length > 0 && (
                    <p className="text-[10px] uppercase tracking-wider text-[#A0A7A3] font-medium px-3 py-2">
                        Recent Campaigns
                    </p>
                )}

                {campaignList.map((c: CampaignListItem) => {
                    const isActive = activeCampaignId === c.campaign_id;
                    return (
                        <button
                            key={c.campaign_id}
                            onClick={() => handleSelectCampaign(c.campaign_id)}
                            title={isOpen ? undefined : c.title}
                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                                isActive
                                    ? "bg-[#F6F4EB] border border-[#EBE7DC]"
                                    : "hover:bg-[#F6F4EB]/60"
                            } ${!isOpen && "justify-center"}`}
                        >
                            {/* Status dot */}
                            <span
                                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                                    statusDot[c.status] ?? "bg-gray-400"
                                }`}
                            />

                            {isOpen && (
                                <div className="flex-1 min-w-0">
                                    <p className={`text-sm truncate ${isActive ? "font-medium text-[#1E2A24]" : "text-[#4A5B50]"}`}>
                                        {c.title}
                                    </p>
                                    <p className="text-[10px] text-[#A0A7A3] mt-0.5">
                                        {formatDate(c.updated_at)}
                                    </p>
                                </div>
                            )}
                        </button>
                    );
                })}

                {isOpen && campaignList.length === 0 && (
                    <div className="px-3 py-8 text-center">
                        <p className="text-xs text-[#A0A7A3]">No campaigns yet</p>
                        <p className="text-[10px] text-[#C4C0B4] mt-1">
                            Start a conversation to create one
                        </p>
                    </div>
                )}
            </nav>

            {/* ── User section ──────────────────────────────────── */}
            <div className="p-4 border-t border-[#EBE7DC]">
                <div className={`flex items-center gap-3 ${!isOpen && "justify-center"}`}>
                    <div className="w-8 h-8 rounded-full bg-[#E26A4A] text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                        {user?.username?.charAt(0)?.toUpperCase() ?? "U"}
                    </div>
                    {isOpen && (
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-[#1E2A24] truncate">
                                {user?.username ?? "User Account"}
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </aside>
    );
}
