"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { CampaignProvider } from "@/lib/campaign-context";
import Sidebar from "@/components/home/sidebar/Sidebar";
import ChatContainer from "@/components/home/chat/ChatContainer";
import GeneratedContent from "@/components/home/content/GeneratedContent";

export default function HomePage() {
    const { user, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && !user) {
            router.push("/auth/login");
        }
    }, [user, loading, router]);

    if (loading || !user) {
        return (
            <div className="flex h-screen w-full items-center justify-center bg-[#F6F4EB]">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#1E2A24]"></div>
            </div>
        );
    }

    return (
        <CampaignProvider>
            <div className="flex h-screen w-full overflow-hidden bg-[#F6F4EB]">
                <Sidebar />
                <ChatContainer />
                <GeneratedContent />
            </div>
        </CampaignProvider>
    );
}
