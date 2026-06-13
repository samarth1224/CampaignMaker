"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import ChatDisplay from "./ChatDisplay";
import ChatInput from "./ChatInput";
import { runAgent, AgentEvent } from "@/lib/agent";
import { useCampaign } from "@/lib/campaign-context";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    /** Optional metadata for non-text events shown in chat */
    eventType?: string;
}

export default function ChatContainer() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const abortRef = useRef<AbortController | null>(null);

    const {
        campaignId,
        setCampaignId,
        campaign,
        fetchCampaign,
        fetchCampaignList,
    } = useCampaign();

    // Sync messages with the active campaign
    useEffect(() => {
        if (!campaign) {
            setMessages([]);
        } else if (campaign.messages && !isStreaming) {
            setMessages(
                campaign.messages.map((m, i) => ({
                    id: `history-${i}`,
                    role: m.role,
                    content: m.content,
                }))
            );
        }
    }, [campaign, isStreaming]);

    /** Append a new assistant-role message to the chat */
    const appendAssistantMessage = useCallback(
        (content: string, eventType?: string) => {
            const msg: Message = {
                id: (Date.now() + Math.random()).toString(),
                role: "assistant",
                content,
                eventType,
            };
            setMessages((prev) => [...prev, msg]);
        },
        []
    );

    /** Update the latest message with the given assistantId */
    const updateAssistantMessage = useCallback(
        (assistantId: string, content: string) => {
            setMessages((prev) =>
                prev.map((m) =>
                    m.id === assistantId ? { ...m, content } : m
                )
            );
        },
        []
    );

    const handleSendMessage = useCallback(
        (content: string) => {
            // ── 1. Add user message immediately ──────────────────
            const userMsg: Message = {
                id: Date.now().toString(),
                role: "user",
                content,
            };
            setMessages((prev) => [...prev, userMsg]);
            setIsStreaming(true);

            // ── 2. Create a placeholder assistant message ────────
            const assistantId = (Date.now() + 1).toString();
            const assistantMsg: Message = {
                id: assistantId,
                role: "assistant",
                content: "",
            };
            setMessages((prev) => [...prev, assistantMsg]);

            // ── 3. Start SSE stream ─────────────────────────────
            abortRef.current = runAgent({
                prompt: content,
                campaignId: campaignId ?? undefined,
                onEvent: (event: AgentEvent) => {
                    switch (event.type) {
                        case "text":
                        case "text_chunk":
                        case "final_response": {
                            const text = event.data?.text ?? "";
                            if (text) {
                                updateAssistantMessage(assistantId, text);
                            }
                            break;
                        }

                        case "tool_call": {
                            const calls = event.data?.calls ?? [];
                            const names = calls
                                .map((c: any) => c.name)
                                .join(", ");
                            appendAssistantMessage(
                                `🔧 Calling: ${names}`,
                                "tool_call"
                            );
                            break;
                        }

                        case "tool_result": {
                            const results = event.data?.results ?? [];
                            const names = results
                                .map((r: any) => r.name)
                                .join(", ");
                            appendAssistantMessage(
                                `✅ Result from: ${names}`,
                                "tool_result"
                            );
                            break;
                        }

                        case "agent_transfer": {
                            const target =
                                event.data?.target_agent ?? "unknown";
                            appendAssistantMessage(
                                `🔄 Transferring to: ${target}`,
                                "agent_transfer"
                            );
                            break;
                        }

                        case "state_update": {
                            // Show a brief notification about state updates
                            const keys = event.data?.state_delta
                                ? Object.keys(event.data.state_delta)
                                : [];
                            if (keys.length > 0) {
                                appendAssistantMessage(
                                    `📋 Updated: ${keys.join(", ")}`,
                                    "state_update"
                                );
                            }
                            break;
                        }

                        case "error": {
                            const errText =
                                event.data?.error_message ??
                                "Something went wrong.";
                            updateAssistantMessage(
                                assistantId,
                                `⚠️ ${errText}`
                            );
                            break;
                        }

                        default:
                            break;
                    }
                },
                onDone: async (cId) => {
                    setIsStreaming(false);
                    if (cId) {
                        setCampaignId(cId);
                        // Fetch the completed campaign data for the content panel
                        await fetchCampaign(cId);
                        // Refresh the sidebar campaign list
                        await fetchCampaignList();
                    }
                },
                onError: (err) => {
                    setIsStreaming(false);
                    updateAssistantMessage(
                        assistantId,
                        `⚠️ ${err.message || "Connection failed."}`
                    );
                },
            });
        },
        [
            campaignId,
            setCampaignId,
            fetchCampaign,
            fetchCampaignList,
            appendAssistantMessage,
            updateAssistantMessage,
        ]
    );

    return (
        <div className="flex-1 flex flex-col h-full bg-[#FCFBF8] relative">
            <header className="h-16 flex items-center justify-between px-6 border-b border-[#EBE7DC] bg-white/50 backdrop-blur-sm z-10">
                <h1 className="font-medium text-[#1E2A24]">Campaign Copilot</h1>
                <div className="flex gap-2 items-center">
                    {isStreaming && (
                        <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium bg-emerald-50 text-emerald-600 rounded-full">
                            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                            Generating
                        </span>
                    )}
                </div>
            </header>

            <ChatDisplay messages={messages} isStreaming={isStreaming} />
            <ChatInput onSendMessage={handleSendMessage} disabled={isStreaming} />
        </div>
    );
}
