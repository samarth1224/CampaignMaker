// TypeScript interfaces mirroring backend schemas for the Generated Content panel

// ── CampaignStrategy (from agent/schemas/CampaignMaker/CampaignMaker.py) ────

export interface Timeline {
    duration_in_weeks: number;
}

export interface TargetAudience {
    age_range: string;
    gender: "All" | "Male" | "Female" | "Non-binary";
    interests: string[];
    demographics: string[];
    income: "Low" | "Medium" | "High";
}

export interface SuccessMetric {
    metric_name: string;
    metric_value: string;
}

export interface Goal {
    goal: string | null;
    success_metrics: SuccessMetric[];
}

export interface PostingStrategy {
    frequency_per_week: number;
    posting_hours: string[];
    posting_days: string[];
}

export interface ContentDirection {
    tone: string | null;
    style: string[] | null;
    visual_theme: string[] | null;
    posting_strategy: PostingStrategy | null;
}

export interface CampaignStrategy {
    name: string | null;
    summary: string | null;
    timeline: Timeline;
    target_audience: TargetAudience;
    key_messages: string[];
    goal: Goal;
    content_direction: ContentDirection;
}

// ── Content (from agent/schemas/ContentGenerator/ContentGenerator.py) ────────

export interface SinglePost {
    name: string;
    platform: string;
    post_text: string;
    has_media: boolean;
    media_name: string | null;
}

export interface PostContent {
    svg_code: string;
    media_name: string;
}

export interface PostCollection {
    platform: string;
    posts: SinglePost[];
}

export interface PlatformContent {
    platform: string;
    posts: PostCollection;
    media: PostContent[];
}

// ── Campaign (from app/models/campaign.py) ──────────────────────────────────

export interface Campaign {
    campaign_id: string;
    user_id: string;
    title: string;
    status: "draft" | "generating" | "completed" | "failed";
    strategy: CampaignStrategy | null;
    content: PlatformContent[];
    messages?: {
        role: "user" | "assistant";
        content: string;
        author?: string;
        timestamp: string;
    }[];
    created_at: string;
    updated_at: string;
}
