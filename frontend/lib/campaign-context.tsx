"use client";

import {
    createContext,
    useContext,
    useState,
    useCallback,
    type ReactNode,
} from "react";
import type {
    Campaign,
    CampaignStrategy,
    PlatformContent,
} from "@/interfaces/campaign.type";

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

/* ── Types ─────────────────────────────────────────────────────────────── */

export interface CampaignListItem {
    campaign_id: string;
    title: string;
    status: string;
    created_at: string;
    updated_at: string;
}

interface CampaignContextValue {
    /** The campaign ID for the current session */
    campaignId: string | null;
    setCampaignId: (id: string | null) => void;

    /** Full campaign data for the Generated Content panel */
    campaign: Campaign | null;
    setCampaign: (c: Campaign | null) => void;

    /** List of user's previous campaigns for the sidebar */
    campaignList: CampaignListItem[];
    setCampaignList: (list: CampaignListItem[]) => void;

    /** Fetch campaigns list from backend */
    fetchCampaignList: () => Promise<void>;

    /** Fetch full campaign by ID */
    fetchCampaign: (id: string) => Promise<void>;

    /** Whether we're currently loading */
    loading: boolean;
}

const CampaignContext = createContext<CampaignContextValue | undefined>(
    undefined
);

/* ── Provider ──────────────────────────────────────────────────────────── */

export function CampaignProvider({ children }: { children: ReactNode }) {
    const [campaignId, setCampaignId] = useState<string | null>(null);
    const [campaign, setCampaign] = useState<Campaign | null>(null);
    const [campaignList, setCampaignList] = useState<CampaignListItem[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchCampaignList = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/campaigns/`, {
                credentials: "include",
            });
            if (res.ok) {
                const data = await res.json();
                setCampaignList(data);
            }
        } catch (err) {
            console.error("Failed to fetch campaign list:", err);
        }
    }, []);

    const fetchCampaign = useCallback(async (id: string) => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/campaigns/${id}`, {
                credentials: "include",
            });
            if (res.ok) {
                const data = await res.json();
                setCampaign(data);
                setCampaignId(id);
            }
        } catch (err) {
            console.error("Failed to fetch campaign:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    return (
        <CampaignContext.Provider
            value={{
                campaignId,
                setCampaignId,
                campaign,
                setCampaign,
                campaignList,
                setCampaignList,
                fetchCampaignList,
                fetchCampaign,
                loading,
            }}
        >
            {children}
        </CampaignContext.Provider>
    );
}

/* ── Hook ──────────────────────────────────────────────────────────────── */

export function useCampaign() {
    const ctx = useContext(CampaignContext);
    if (!ctx) {
        throw new Error("useCampaign must be used within a <CampaignProvider>");
    }
    return ctx;
}
