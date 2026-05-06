/**
 * POST to an SSE chat endpoint and invoke on_delta for each decoded text fragment.
 */
export async function stream_chat_sse(
  url: string,
  body: Record<string, unknown>,
  signal: AbortSignal,
  on_delta: (text: string) => void,
): Promise<void> {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const reader = res.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }
  const decoder = new TextDecoder();
  let buffer = "";

  /**
   * Parse complete SSE events (blocks separated by blank line) from buffer.
   *
   * @returns True when a terminal `[DONE]` data line was seen.
   */
  function flush_sse_events(): boolean {
    let finished = false;
    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const raw_event = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      for (const line of raw_event.split("\n")) {
        const trimmed = line.replace(/\r$/, "");
        if (!trimmed.startsWith("data:")) continue;
        const payload = trimmed.slice(5).trimStart();
        if (payload === "[DONE]") {
          finished = true;
          continue;
        }
        try {
          const piece = JSON.parse(payload) as unknown;
          if (typeof piece === "string") {
            on_delta(piece);
          }
        } catch {
          /* skip malformed data lines */
        }
      }
    }
    return finished;
  }

  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value ?? new Uint8Array(), { stream: !done });
    const finished = flush_sse_events();
    if (finished) {
      await reader.cancel();
      break;
    }
    if (done) {
      break;
    }
  }
}
