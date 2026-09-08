"use client";
import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface MarkdownRendererProps {
  content: string;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ className, children, ...props }: any) {
          const match = /language-(\w+)/.exec(className || "");
          const isBlock = match;
          return isBlock ? (
            <div className="relative group my-2">
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
                className="!rounded-xl !text-xs !bg-black/80 !border !border-slate-800 !m-0"
                {...props}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            </div>
          ) : (
            <code className="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 text-xs font-mono border border-slate-700" {...props}>
              {children}
            </code>
          );
        },
        p: ({ children }) => <p className="text-xs text-slate-300 my-1">{children}</p>,
        h1: ({ children }) => <h1 className="text-sm font-bold text-slate-100 my-2">{children}</h1>,
        h2: ({ children }) => <h2 className="text-sm font-semibold text-slate-200 my-2">{children}</h2>,
        h3: ({ children }) => <h3 className="text-xs font-semibold text-slate-200 my-1.5">{children}</h3>,
        h4: ({ children }) => <h4 className="text-xs font-medium text-slate-300 my-1.5">{children}</h4>,
        h5: ({ children }) => <h5 className="text-xs text-slate-400 my-1">{children}</h5>,
        h6: ({ children }) => <h6 className="text-[11px] text-slate-500 my-1 uppercase">{children}</h6>,
        ul: ({ children }) => <ul className="list-disc list-inside text-xs text-slate-300 my-1.5 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-inside text-xs text-slate-300 my-1.5 space-y-1">{children}</ol>,
        li: ({ children }) => <li>{children}</li>,
        blockquote: ({ children }) => <blockquote className="border-l-2 border-emerald-500/50 pl-3 my-2 text-slate-400 italic text-xs bg-emerald-950/20 py-1 rounded-r">{children}</blockquote>,
        table: ({ children }) => <div className="overflow-x-auto my-2 border border-slate-800 rounded-lg"><table className="min-w-full divide-y divide-slate-800 text-xs">{children}</table></div>,
        thead: ({ children }) => <thead className="bg-slate-900/80">{children}</thead>,
        tbody: ({ children }) => <tbody className="divide-y divide-slate-800/60 bg-slate-900/40">{children}</tbody>,
        tr: ({ children }) => <tr>{children}</tr>,
        th: ({ children }) => <th className="px-3 py-2 text-left text-[11px] font-semibold text-slate-300 uppercase tracking-wider">{children}</th>,
        td: ({ children }) => <td className="px-3 py-2 text-slate-400 whitespace-nowrap">{children}</td>,
        a: ({ children, href }) => <a href={href} className="text-cyan-400 hover:text-cyan-300 hover:underline">{children}</a>,
        strong: ({ children }) => <strong className="font-semibold text-slate-200">{children}</strong>,
        em: ({ children }) => <em className="italic text-slate-400">{children}</em>,
        hr: () => <hr className="my-3 border-slate-800" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
