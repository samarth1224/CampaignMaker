/**
 * Agent API — connects to the SSE streaming endpoint.
 *
 * All ADK-event-level details are abstracted behind a simple callback
 * interface so the UI components never deal with raw SSE frames.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

/** Shape of a single parsed SSE event from the backend. */
export interface AgentEvent {
  type:
  | "text"
  | "text_chunk"
  | "tool_call"
  | "tool_result"
  | "state_update"
  | "agent_transfer"
  | "final_response"
  | "error"
  | "done";
  author: string;
  data: Record<string, any>;
}

export interface RunAgentOptions {
  prompt: string;
  campaignId?: string;
  /** Called for every parsed SSE event. */
  onEvent: (event: AgentEvent) => void;
  /** Called once the stream ends (after [DONE]). */
  onDone?: (campaignId: string | null) => void;
  /** Called if the connection itself fails. */
  onError?: (error: Error) => void;
}

/**
 * Start an agent run via the SSE endpoint.
 *
 * Returns an `AbortController` so the caller can cancel mid-stream
 * (e.g. if the user navigates away).
 */
export function runAgent(options: RunAgentOptions): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_BASE}/agent/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: options.prompt,
          campaign_id: options.campaignId ?? null,
        }),
        credentials: "include",
        signal: controller.signal,
      });

      if (!res.ok) {
        const errBody = await res.json().catch(() => ({ detail: "Agent request failed" }));
        throw new Error(errBody.detail || `HTTP ${res.status}`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";
      let lastCampaignId: string | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE frames are separated by double newlines
        const frames = buffer.split("\n\n");
        // Keep the last (possibly incomplete) chunk in the buffer
        buffer = frames.pop() || "";

        for (const frame of frames) {
          const line = frame.trim();
          if (!line.startsWith("data: ")) continue;

          const payload = line.slice(6); // strip "data: "

          try {
            const event: AgentEvent = JSON.parse(payload);
            options.onEvent(event);

            if (event.type === "done") {
              lastCampaignId = event.data?.campaign_id ?? null;
            }
          } catch {
            // Non-JSON data line — ignore
          }
        }
      }

      options.onDone?.(lastCampaignId);
    } catch (err: any) {
      if (err.name === "AbortError") return; // user cancelled
      options.onError?.(err);
    }
  })();

  return controller;
}
