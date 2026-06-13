"use client";

import { useEffect, useRef } from "react";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    eventType?: string;
}

interface ChatDisplayProps {
    messages: Message[];
    isStreaming?: boolean;
}

const EVENT_STYLES: Record<string, string> = {
    tool_call:
        "bg-amber-50 border-amber-200 text-amber-800",
    tool_result:
        "bg-emerald-50 border-emerald-200 text-emerald-800",
    agent_transfer:
        "bg-blue-50 border-blue-200 text-blue-800",
    state_update:
        "bg-violet-50 border-violet-200 text-violet-800",
};

export default function ChatDisplay({ messages, isStreaming }: ChatDisplayProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    return (
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
            {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto">
                    <div className="w-16 h-16 bg-white rounded-2xl shadow-sm border border-[#EBE7DC] flex items-center justify-center mb-6 text-[#E26A4A]">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    </div>
                    <h2 className="text-2xl font-serif font-medium text-[#1E2A24] mb-2">How can I help you today?</h2>
                    <p className="text-[#6B726F] text-sm">Create a new marketing campaign, generate copy, or ask for strategy advice.</p>
                </div>
            ) : (
                <>
                    {messages.map((msg) => {
                        // Compact system event bubble (tool call, transfer, etc.)
                        if (msg.role === "assistant" && msg.eventType && EVENT_STYLES[msg.eventType]) {
                            return (
                                <div key={msg.id} className="flex justify-center">
                                    <div
                                        className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full border text-xs font-medium ${EVENT_STYLES[msg.eventType]}`}
                                    >
                                        {msg.content}
                                    </div>
                                </div>
                            );
                        }

                        // Regular user / assistant message
                        return (
                            <div key={msg.id} className={`flex gap-4 max-w-3xl mx-auto ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-medium ${msg.role === "user" ? "bg-[#1E2A24] text-white" : "bg-[#E26A4A] text-white"}`}>
                                    {msg.role === "user" ? "U" : "AI"}
                                </div>
                                <div className={`px-5 py-3.5 rounded-2xl max-w-[80%] ${msg.role === "user" ? "bg-[#1E2A24] text-white rounded-tr-sm" : "bg-white border border-[#EBE7DC] text-[#1E2A24] rounded-tl-sm shadow-sm"}`}>
                                    {msg.content ? (
                                        <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                                    ) : (
                                        // Typing indicator for empty assistant messages (streaming)
                                        msg.role === "assistant" && isStreaming && (
                                            <div className="flex items-center gap-1 py-1">
                                                <span className="w-2 h-2 bg-[#A0A7A3] rounded-full animate-bounce [animation-delay:0ms]" />
                                                <span className="w-2 h-2 bg-[#A0A7A3] rounded-full animate-bounce [animation-delay:150ms]" />
                                                <span className="w-2 h-2 bg-[#A0A7A3] rounded-full animate-bounce [animation-delay:300ms]" />
                                            </div>
                                        )
                                    )}
                                </div>
                            </div>
                        );
                    })}
                    <div ref={bottomRef} />
                </>
            )}
        </div>
    );
}
