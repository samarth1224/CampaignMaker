"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { type AgentEvent, runAgent } from "@/lib/agent";
import { useCampaign } from "@/lib/campaign-context";
import { uploadDocuments } from "@/lib/documents";

import ChatDisplay from "./ChatDisplay";
import ChatInput from "./ChatInput";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  eventType?: string;
}

export default function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const {
    campaignId,
    setCampaignId,
    campaign,
    fetchCampaign,
    fetchCampaignList,
  } = useCampaign();

  useEffect(() => {
    if (!campaign) {
      setMessages([]);
    } else if (!isStreaming) {
      setMessages(
        (campaign.messages ?? []).map((message, index) => ({
          id: `history-${index}`,
          role: message.role,
          content: message.content,
        })),
      );
    }
  }, [campaign, isStreaming]);

  useEffect(() => () => abortRef.current?.abort(), []);

  const appendAssistantMessage = useCallback(
    (content: string, eventType?: string) => {
      setMessages((current) => [
        ...current,
        { id: createMessageId("event"), role: "assistant", content, eventType },
      ]);
    },
    [],
  );

  const updateAssistantMessage = useCallback((id: string, content: string) => {
    setMessages((current) =>
      current.map((message) =>
        message.id === id ? { ...message, content } : message,
      ),
    );
  }, []);

  const appendAssistantText = useCallback((id: string, text: string) => {
    setMessages((current) =>
      current.map((message) =>
        message.id === id ? { ...message, content: `${message.content}${text}` } : message,
      ),
    );
  }, []);

  const handleSendMessage = useCallback(
    (content: string) => {
      const prompt = content.trim();
      if (!prompt || isStreaming) return;

      const assistantId = createMessageId("assistant");
      setMessages((current) => [
        ...current,
        { id: createMessageId("user"), role: "user", content: prompt },
        { id: assistantId, role: "assistant", content: "" },
      ]);
      setIsStreaming(true);

      abortRef.current = runAgent({
        prompt,
        campaignId: campaignId ?? undefined,
        onEvent: (event) =>
          handleAgentEvent({
            event,
            assistantId,
            updateAssistantMessage,
            appendAssistantText,
            appendAssistantMessage,
          }),
        onDone: async (completedCampaignId) => {
          abortRef.current = null;
          setIsStreaming(false);
          if (!completedCampaignId) return;

          setCampaignId(completedCampaignId);
          await Promise.all([
            fetchCampaign(completedCampaignId),
            fetchCampaignList(),
          ]);
        },
        onError: (error) => {
          abortRef.current = null;
          setIsStreaming(false);
          updateAssistantMessage(assistantId, `⚠️ ${error.message}`);
        },
      });
    },
    [
      appendAssistantMessage,
      appendAssistantText,
      campaignId,
      fetchCampaign,
      fetchCampaignList,
      isStreaming,
      setCampaignId,
      updateAssistantMessage,
    ],
  );

  const handleUploadDocuments = useCallback(
    async (files: File[]) => {
      if (isUploading || isStreaming) return;

      setIsUploading(true);
      setUploadStatus(
        `Indexing ${files.length === 1 ? files[0].name : `${files.length} documents`}…`,
      );
      try {
        const uploaded = await uploadDocuments(files, campaignId ?? undefined);
        const chunks = uploaded.reduce((total, document) => total + document.chunk_count, 0);
        setUploadStatus(
          `${uploaded.length === 1 ? uploaded[0].filename : `${uploaded.length} documents`} ready for campaign context (${chunks} chunks indexed).`,
        );
      } catch (error) {
        const message = error instanceof Error ? error.message : "Document upload failed.";
        setUploadStatus(`Upload failed: ${message}`);
      } finally {
        setIsUploading(false);
      }
    },
    [campaignId, isStreaming, isUploading],
  );

  return (
    <div className="flex-1 flex flex-col h-full bg-[#FCFBF8] relative">
      <header className="h-16 flex items-center justify-between px-6 border-b border-[#EBE7DC] bg-white/50 backdrop-blur-sm z-10">
        <h1 className="font-medium text-[#1E2A24]">Campaign Copilot</h1>
        {isStreaming && (
          <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium bg-emerald-50 text-emerald-600 rounded-full">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
            Generating
          </span>
        )}
      </header>

      <ChatDisplay messages={messages} isStreaming={isStreaming} />
      <ChatInput
        onSendMessage={handleSendMessage}
        onUploadDocuments={handleUploadDocuments}
        disabled={isStreaming}
        isUploading={isUploading}
        uploadStatus={uploadStatus}
      />
    </div>
  );
}

function handleAgentEvent({
  event,
  assistantId,
  updateAssistantMessage,
  appendAssistantText,
  appendAssistantMessage,
}: {
  event: AgentEvent;
  assistantId: string;
  updateAssistantMessage: (id: string, content: string) => void;
  appendAssistantText: (id: string, text: string) => void;
  appendAssistantMessage: (content: string, eventType: string) => void;
}): void {
  switch (event.type) {
    case "text_chunk": {
      appendAssistantText(assistantId, getText(event));
      break;
    }
    case "text":
    case "final_response":
      updateAssistantMessage(assistantId, getText(event));
      break;
    case "tool_call":
      appendAssistantMessage(`🔧 Calling: ${getNames(event, "calls")}`, "tool_call");
      break;
    case "tool_result":
      appendAssistantMessage(`✅ Result from: ${getNames(event, "results")}`, "tool_result");
      break;
    case "agent_transfer":
      appendAssistantMessage(
        `🔄 Transferring to: ${getString(event.data.target_agent, "unknown")}`,
        "agent_transfer",
      );
      break;
    case "state_update": {
      const state = event.data.state_delta;
      const keys = isRecord(state) ? Object.keys(state) : [];
      if (keys.length > 0) {
        appendAssistantMessage(`📋 Updated: ${keys.join(", ")}`, "state_update");
      }
      break;
    }
    case "error":
      updateAssistantMessage(
        assistantId,
        `⚠️ ${getString(event.data.error_message, "Something went wrong.")}`,
      );
      break;
  }
}

function getText(event: AgentEvent): string {
  return getString(event.data.text);
}

function getNames(event: AgentEvent, key: "calls" | "results"): string {
  const values = event.data[key];
  if (!Array.isArray(values)) return "the agent";

  const names = values.flatMap((value) => {
    return isRecord(value) && typeof value.name === "string" ? [value.name] : [];
  });
  return names.join(", ") || "the agent";
}

function getString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function createMessageId(prefix: string): string {
  return `${prefix}-${globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`}`;
}
