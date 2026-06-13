"use client";
import { useState } from "react";

export default function ChatInput({ onSendMessage, disabled }: { onSendMessage: (msg: string) => void; disabled?: boolean }) {
    const [input, setInput] = useState("");

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || disabled) return;
        onSendMessage(input);
        setInput("");
    };

    return (
        <div className="p-4 md:px-8 md:pb-8">
            <div className="max-w-3xl mx-auto relative">
                <form onSubmit={handleSubmit} className="relative flex items-end bg-white border border-[#EBE7DC] rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-[#E26A4A]/20 focus-within:border-[#E26A4A] transition-all p-2">
                    <button type="button" className="p-2 text-[#A0A7A3] hover:text-[#1E2A24] transition-colors rounded-xl flex-shrink-0">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
                    </button>
                    
                    <textarea 
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Message CampaignMaker AI..."
                        className="flex-1 max-h-32 min-h-[44px] bg-transparent resize-none py-3 px-2 text-[#1E2A24] placeholder:text-[#A0A7A3] focus:outline-none"
                        rows={1}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit(e);
                            }
                        }}
                    />

                    <button 
                        type="submit" 
                        disabled={!input.trim() || disabled}
                        className="p-2 bg-[#1E2A24] text-white rounded-xl hover:bg-[#2a3a31] transition-colors disabled:opacity-50 disabled:hover:bg-[#1E2A24] flex-shrink-0 m-1"
                    >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    </button>
                </form>
                <div className="text-center mt-2">
                    <span className="text-[11px] text-[#A0A7A3]">CampaignMaker AI can make mistakes. Consider verifying important information.</span>
                </div>
            </div>
        </div>
    );
}
