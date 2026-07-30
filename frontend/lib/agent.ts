/** Utilities for consuming the agent's server-sent event stream. */

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

const AGENT_EVENT_TYPES = [
  "text",
  "text_chunk",
  "tool_call",
  "tool_result",
  "state_update",
  "agent_transfer",
  "final_response",
  "error",
  "done",
] as const;

export type AgentEventType = (typeof AGENT_EVENT_TYPES)[number];

export interface AgentEvent {
  type: AgentEventType;
  author: string;
  data: Record<string, unknown>;
}

export interface RunAgentOptions {
  prompt: string;
  campaignId?: string;
  onEvent: (event: AgentEvent) => void;
  onDone?: (campaignId: string | null) => void;
  onError?: (error: Error) => void;
}

/** Start an agent run and return a controller the caller can use to cancel it. */
export function runAgent(options: RunAgentOptions): AbortController {
  const controller = new AbortController();
  void consumeAgentStream(options, controller.signal);
  return controller;
}

async function consumeAgentStream(
  options: RunAgentOptions,
  signal: AbortSignal,
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/agent/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: options.prompt,
        campaign_id: options.campaignId ?? null,
      }),
      credentials: "include",
      signal,
    });

    if (!response.ok) {
      throw new Error(await getResponseError(response));
    }
    if (!response.body) {
      throw new Error("The agent response did not include a stream.");
    }

    const campaignId = await readSseStream(response.body, options.onEvent);
    options.onDone?.(campaignId);
  } catch (error) {
    if (signal.aborted) return;
    options.onError?.(toError(error));
  }
}

async function readSseStream(
  stream: ReadableStream<Uint8Array>,
  onEvent: RunAgentOptions["onEvent"],
): Promise<string | null> {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let campaignId: string | null = null;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split("\n\n");
      buffer = frames.pop() ?? "";

      for (const frame of frames) {
        campaignId = dispatchFrame(frame, onEvent) ?? campaignId;
      }
    }

    buffer += decoder.decode();
    return dispatchFrame(buffer, onEvent) ?? campaignId;
  } finally {
    reader.releaseLock();
  }
}

function dispatchFrame(
  frame: string,
  onEvent: RunAgentOptions["onEvent"],
): string | null {
  const payload = frame
    .split("\n")
    .filter((line) => line.startsWith("data: "))
    .map((line) => line.slice(6))
    .join("\n");
  if (!payload) return null;

  try {
    const event = JSON.parse(payload) as unknown;
    if (!isAgentEvent(event)) return null;
    onEvent(event);
    return event.type === "done" && typeof event.data.campaign_id === "string"
      ? event.data.campaign_id
      : null;
  } catch {
    return null;
  }
}

function isAgentEvent(value: unknown): value is AgentEvent {
  if (!isRecord(value) || !isRecord(value.data) || typeof value.author !== "string") {
    return false;
  }
  return AGENT_EVENT_TYPES.some((eventType) => eventType === value.type);
}

async function getResponseError(response: Response): Promise<string> {
  try {
    const payload = await response.json();
    if (isRecord(payload) && typeof payload.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Fall back to the HTTP status below when the body is not JSON.
  }
  return `Agent request failed (HTTP ${response.status}).`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function toError(value: unknown): Error {
  return value instanceof Error ? value : new Error("Agent connection failed.");
}
