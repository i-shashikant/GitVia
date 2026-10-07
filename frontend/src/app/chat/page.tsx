"use client";

import { useEffect, useState } from "react";
import { fetchChatHistory, sendChatMessage } from "@/lib/api";
import { 
  MessageSquareCode, 
  Send, 
  Sparkles, 
  Bot, 
  User, 
  HelpCircle,
  ArrowRight
} from "lucide-react";

export default function ChatPage() {
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([
    {
      role: "assistant",
      content:
        "I answer from your cached GitHub analysis — scores, gaps, and repos. Ask about internship readiness, resume projects, or what to build next.",
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchChatHistory()
      .then((history) => {
        if (Array.isArray(history) && history.length > 0) {
          setMessages(
            history.map((item: { role: string; content: string }) => ({
              role: item.role,
              content: item.content,
            }))
          );
        }
      })
      .catch(() => {
        // Unauthenticated users keep the default greeting.
      });
  }, []);

  const samplePrompts = [
    "Am I ready for backend internships?",
    "Which of my projects should I put on my resume?",
    "Should I learn Kubernetes?",
    "Why is my GitHub score low?",
    "What does my latest job match say?",
    "What should I build next?"
  ];

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || loading) return;

    const newMsgs = [...messages, { role: "user", content: query }];
    setMessages(newMsgs);
    if (!textToSend) setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(query);
      setMessages([...newMsgs, { role: "assistant", content: res.response }]);
    } catch (err) {
      console.error(err);
      setMessages([
        ...newMsgs,
        {
          role: "assistant",
          content:
            "I couldn't reach the career assistant right now. Check that the FastAPI backend is running and that your GitHub session is still connected.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          <MessageSquareCode className="h-7 w-7 text-cyan-400" />
          AI Career Assistant
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Context-grounded career AI reasoning over your actual GitHub code, resume mismatches, and target job requirements.
        </p>
      </div>

      {/* Suggested Quick Questions */}
      <div className="flex flex-wrap gap-2">
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            className="flex items-center gap-1.5 rounded-full border border-gray-800 bg-gray-900/80 px-3.5 py-1.5 text-xs text-gray-300 hover:border-cyan-500/50 hover:text-cyan-300 transition-colors"
          >
            <HelpCircle className="h-3.5 w-3.5 text-cyan-400" />
            <span>{prompt}</span>
          </button>
        ))}
      </div>

      {/* Chat Messages Container */}
      <div className="rounded-2xl border border-gray-800 bg-gray-900/60 p-6 min-h-[420px] flex flex-col justify-between space-y-6">
        <div className="space-y-4 overflow-y-auto max-h-[500px] pr-2">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-3 text-xs leading-relaxed ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {m.role === "assistant" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan-950 border border-cyan-800 text-cyan-400">
                  <Bot className="h-4 w-4" />
                </div>
              )}

              <div
                className={`max-w-2xl rounded-2xl p-4 ${
                  m.role === "user"
                    ? "bg-cyan-600 text-white rounded-tr-none font-medium"
                    : "bg-gray-900 border border-gray-800 text-gray-200 rounded-tl-none space-y-2 whitespace-pre-wrap"
                }`}
              >
                {m.content}
              </div>

              {m.role === "user" && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-800 border border-gray-700 text-gray-300">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs text-cyan-400 italic">
              <Sparkles className="h-4 w-4 animate-spin" />
              <span>Analyzing profile context and generating response...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="flex items-center gap-2 border-t border-gray-800 pt-4">
          <input
            type="text"
            placeholder="Ask anything about your code quality, resume alignment, or career path..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            className="flex-1 rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-xs text-white placeholder-gray-500 focus:border-cyan-500 focus:outline-none"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="flex items-center justify-center rounded-xl bg-cyan-500 p-3 text-black hover:bg-cyan-400 disabled:opacity-50 transition-all"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
