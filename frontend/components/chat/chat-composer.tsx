"use client";

import { KeyboardEvent, useState } from "react";
import { Mic, Paperclip, SendHorizonal } from "lucide-react";

type ChatComposerProps = {
  onSend?: (text: string) => void;
  sending?: boolean;
};

export function ChatComposer({ onSend, sending = false }: ChatComposerProps) {
  const [value, setValue] = useState("");

  const submit = () => {
    if (sending || !value.trim()) {
      return;
    }
    onSend?.(value.trim());
    setValue("");
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="rounded-[2rem] border border-white/60 bg-white/85 p-4 shadow-soft backdrop-blur-xl dark:border-sage-800/70 dark:bg-sage-950/78">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end">
        <textarea
          className="min-h-[110px] flex-1 resize-none rounded-[1.5rem] border border-sage-100 bg-sage-50/50 px-4 py-4 text-sm text-ink outline-none placeholder:text-sage-600/55 dark:border-sage-800 dark:bg-sage-900/70 dark:text-sand-50 dark:placeholder:text-sand-50/40"
          placeholder="Describe what you’re feeling. Safebond can combine recent emotional context, memory recall, and safety-aware support."
          value={value}
          disabled={sending}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={handleKeyDown}
        />
        <div className="flex items-center gap-3">
          <button
            className="flex h-12 w-12 items-center justify-center rounded-full border border-sage-200 bg-sage-50 text-sage-800 disabled:opacity-50 dark:border-sage-700 dark:bg-sage-900 dark:text-sand-50"
            disabled={sending}
            type="button"
          >
            <Paperclip className="h-4 w-4" />
          </button>
          <button
            className="flex h-12 w-12 items-center justify-center rounded-full border border-sage-200 bg-sage-50 text-sage-800 disabled:opacity-50 dark:border-sage-700 dark:bg-sage-900 dark:text-sand-50"
            disabled={sending}
            type="button"
          >
            <Mic className="h-4 w-4" />
          </button>
          <button
            className="flex items-center gap-2 rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white shadow-soft disabled:opacity-60 dark:bg-sand-100 dark:text-sage-950"
            disabled={sending || !value.trim()}
            onClick={submit}
            type="button"
          >
            {sending ? "Sending..." : "Send"}
            <SendHorizonal className="h-4 w-4" />
          </button>
        </div>
      </div>
      <p className="mt-3 text-xs text-sage-700/70 dark:text-sand-50/55">
        Press <span className="font-semibold text-sage-900 dark:text-sand-50">Enter</span> to send and{" "}
        <span className="font-semibold text-sage-900 dark:text-sand-50">Shift + Enter</span> for a new line.
      </p>
    </div>
  );
}
