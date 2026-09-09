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
            <div className="relative group my-4 shadow-sm border border-[var(--border)] rounded-[12px] overflow-hidden">
              <SyntaxHighlighter
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
                className="!m-0 !bg-[#1A1A1A] !text-[13px] !p-4 !font-mono"
                {...props}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            </div>
          ) : (
            <code className="px-1.5 py-0.5 mx-0.5 rounded-md bg-[var(--accent-light)] text-[var(--foreground)] text-[13px] font-mono border border-[var(--border)]" {...props}>
              {children}
            </code>
          );
        },
        p: ({ children }) => <p className="text-[15px] text-[var(--foreground)] leading-relaxed my-2">{children}</p>,
        h1: ({ children }) => <h1 className="text-[20px] font-semibold text-[var(--foreground)] tracking-tight my-4">{children}</h1>,
        h2: ({ children }) => <h2 className="text-[18px] font-semibold text-[var(--foreground)] tracking-tight my-3">{children}</h2>,
        h3: ({ children }) => <h3 className="text-[16px] font-medium text-[var(--foreground)] my-2">{children}</h3>,
        h4: ({ children }) => <h4 className="text-[15px] font-medium text-[var(--foreground)] my-2">{children}</h4>,
        h5: ({ children }) => <h5 className="text-[14px] text-[var(--foreground-muted)] my-2">{children}</h5>,
        h6: ({ children }) => <h6 className="text-[12px] text-[var(--foreground-muted)] my-1 uppercase tracking-wider">{children}</h6>,
        ul: ({ children }) => <ul className="list-disc list-outside ml-5 text-[15px] text-[var(--foreground)] leading-relaxed my-3 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-outside ml-5 text-[15px] text-[var(--foreground)] leading-relaxed my-3 space-y-1">{children}</ol>,
        li: ({ children }) => <li>{children}</li>,
        blockquote: ({ children }) => <blockquote className="border-l-[3px] border-[var(--border-hover)] pl-4 my-4 text-[var(--foreground-muted)] italic text-[15px] bg-[var(--sidebar-bg)]/50 py-2 rounded-r-lg">{children}</blockquote>,
        table: ({ children }) => <div className="overflow-x-auto my-4 shadow-sm border border-[var(--border)] rounded-[12px]"><table className="min-w-full divide-y divide-[var(--border)] text-[14px]">{children}</table></div>,
        thead: ({ children }) => <thead className="bg-[var(--sidebar-bg)]">{children}</thead>,
        tbody: ({ children }) => <tbody className="divide-y divide-[var(--border)] bg-[var(--input-bg)]">{children}</tbody>,
        tr: ({ children }) => <tr className="hover:bg-[var(--sidebar-bg)]/30 transition-colors">{children}</tr>,
        th: ({ children }) => <th className="px-4 py-3 text-left text-[12px] font-medium text-[var(--foreground-muted)] uppercase tracking-wider">{children}</th>,
        td: ({ children }) => <td className="px-4 py-3 text-[var(--foreground)] whitespace-nowrap">{children}</td>,
        a: ({ children, href }) => <a href={href} className="text-blue-600 hover:text-blue-700 underline underline-offset-2 decoration-blue-600/30 hover:decoration-blue-700 transition-colors">{children}</a>,
        strong: ({ children }) => <strong className="font-semibold text-[var(--foreground)]">{children}</strong>,
        em: ({ children }) => <em className="italic text-[var(--foreground-muted)]">{children}</em>,
        hr: () => <hr className="my-6 border-[var(--border)]" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
