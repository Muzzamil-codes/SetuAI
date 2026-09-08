(globalThis["TURBOPACK"] || (globalThis["TURBOPACK"] = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/app/trace/[taskId]/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>TracePage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$TraceStream$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/TraceStream.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ArtifactDownloadCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ArtifactDownloadCard.tsx [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$ws$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/ws-client.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
function TracePage() {
    _s();
    const params = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useParams"])();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const taskId = params?.taskId;
    const [theme, setTheme] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])("dark");
    const [events, setEvents] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [artifacts, setArtifacts] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])([]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "TracePage.useEffect": ()=>{
            const saved = localStorage.getItem("setu-theme");
            if (saved) setTheme(saved);
        }
    }["TracePage.useEffect"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "TracePage.useEffect": ()=>{
            if (!taskId) return;
            const cleanup = (0, __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$ws$2d$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["connectWebSocket"])(taskId, {
                "TracePage.useEffect.cleanup": (evt)=>{
                    setEvents({
                        "TracePage.useEffect.cleanup": (prev)=>[
                                ...prev,
                                evt
                            ]
                    }["TracePage.useEffect.cleanup"]);
                    if (evt.step === "done" && evt.payload.artifacts) {
                        setArtifacts(evt.payload.artifacts);
                    }
                }
            }["TracePage.useEffect.cleanup"]);
            return ({
                "TracePage.useEffect": ()=>cleanup()
            })["TracePage.useEffect"];
        }
    }["TracePage.useEffect"], [
        taskId
    ]);
    const isBgDark = theme === "dark" || theme === "elevated";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        className: `min-h-screen p-6 flex flex-col items-center transition-colors duration-300 ${isBgDark ? "bg-black text-white" : "bg-gray-100 text-gray-900"}`,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "w-full max-w-3xl space-y-4",
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: "flex justify-between items-center",
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                                    className: "text-xl font-bold",
                                    children: "Agent Execution Monitor"
                                }, void 0, false, {
                                    fileName: "[project]/app/trace/[taskId]/page.tsx",
                                    lineNumber: 48,
                                    columnNumber: 13
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                    className: `text-xs font-mono ${isBgDark ? "text-zinc-400" : "text-gray-500"}`,
                                    children: [
                                        "Task ID: ",
                                        taskId
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/app/trace/[taskId]/page.tsx",
                                    lineNumber: 49,
                                    columnNumber: 13
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/app/trace/[taskId]/page.tsx",
                            lineNumber: 47,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                            onClick: ()=>router.push("/"),
                            className: `text-xs px-3 py-1.5 rounded transition border ${isBgDark ? "bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border-zinc-700" : "bg-white hover:bg-gray-100 text-gray-800 border-gray-300"}`,
                            children: "← Back"
                        }, void 0, false, {
                            fileName: "[project]/app/trace/[taskId]/page.tsx",
                            lineNumber: 53,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/app/trace/[taskId]/page.tsx",
                    lineNumber: 46,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$TraceStream$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                    events: events,
                    theme: theme
                }, void 0, false, {
                    fileName: "[project]/app/trace/[taskId]/page.tsx",
                    lineNumber: 65,
                    columnNumber: 9
                }, this),
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ArtifactDownloadCard$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"], {
                    artifacts: artifacts,
                    theme: theme
                }, void 0, false, {
                    fileName: "[project]/app/trace/[taskId]/page.tsx",
                    lineNumber: 66,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/app/trace/[taskId]/page.tsx",
            lineNumber: 45,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/app/trace/[taskId]/page.tsx",
        lineNumber: 40,
        columnNumber: 5
    }, this);
}
_s(TracePage, "Njzt8cYZ8t9ttu1RNcCwR2oQoaY=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useParams"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRouter"]
    ];
});
_c = TracePage;
var _c;
__turbopack_context__.k.register(_c, "TracePage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/ArtifactDownloadCard.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>ArtifactDownloadCard
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
"use client";
;
function ArtifactDownloadCard({ artifacts, theme = "elevated" }) {
    if (!artifacts || artifacts.length === 0) return null;
    const isCardWhite = theme === "light" || theme === "elevated";
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: `p-4 rounded-xl border space-y-3 shadow-md transition-colors ${isCardWhite ? "bg-white border-gray-200" : "bg-zinc-950 border-zinc-800"}`,
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                className: `font-semibold text-sm ${isCardWhite ? "text-emerald-700" : "text-emerald-400"}`,
                children: "Generated Artifacts (Confidential On-Prem)"
            }, void 0, false, {
                fileName: "[project]/components/ArtifactDownloadCard.tsx",
                lineNumber: 24,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "space-y-2",
                children: artifacts.map((art, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: `flex justify-between items-center p-2.5 rounded-lg border ${isCardWhite ? "bg-gray-50 border-gray-200" : "bg-zinc-900 border-zinc-800"}`,
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "flex items-center gap-2",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: `text-xs font-bold uppercase px-2 py-0.5 rounded border ${isCardWhite ? "bg-blue-50 text-blue-700 border-blue-200" : "bg-blue-950 text-blue-400 border-blue-800"}`,
                                        children: art.type
                                    }, void 0, false, {
                                        fileName: "[project]/components/ArtifactDownloadCard.tsx",
                                        lineNumber: 38,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                        className: `text-xs font-medium ${isCardWhite ? "text-gray-800" : "text-zinc-200"}`,
                                        children: art.filename
                                    }, void 0, false, {
                                        fileName: "[project]/components/ArtifactDownloadCard.tsx",
                                        lineNumber: 47,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/components/ArtifactDownloadCard.tsx",
                                lineNumber: 37,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("a", {
                                href: `/${art.path}`,
                                download: art.filename,
                                className: "text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-3 py-1.5 rounded-md transition shadow",
                                children: "Download"
                            }, void 0, false, {
                                fileName: "[project]/components/ArtifactDownloadCard.tsx",
                                lineNumber: 51,
                                columnNumber: 13
                            }, this)
                        ]
                    }, i, true, {
                        fileName: "[project]/components/ArtifactDownloadCard.tsx",
                        lineNumber: 29,
                        columnNumber: 11
                    }, this))
            }, void 0, false, {
                fileName: "[project]/components/ArtifactDownloadCard.tsx",
                lineNumber: 27,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/components/ArtifactDownloadCard.tsx",
        lineNumber: 17,
        columnNumber: 5
    }, this);
}
_c = ArtifactDownloadCard;
var _c;
__turbopack_context__.k.register(_c, "ArtifactDownloadCard");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/TraceStream.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>TraceStream
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
"use client";
;
function TraceStream({ events, theme = "dark" }) {
    const isCardWhite = theme === "light" || theme === "elevated";
    const textColor = isCardWhite ? "text-gray-700" : "text-zinc-200";
    const renderDetails = (evt)=>{
        const p = evt.payload || {};
        switch(evt.step.toLowerCase()){
            case "classify":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: `text-xs ${textColor}`,
                    children: [
                        "Task type: ",
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                            children: p.task_type || "unknown"
                        }, void 0, false, {
                            fileName: "[project]/components/TraceStream.tsx",
                            lineNumber: 21,
                            columnNumber: 24
                        }, this),
                        p.selected_model?.name && ` → Model: ${p.selected_model.name}`
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 20,
                    columnNumber: 11
                }, this);
            case "plan":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: `text-xs ${textColor}`,
                    children: [
                        p.plan || "Planning...",
                        p.retry_count > 0 && ` (retry #${p.retry_count})`
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 27,
                    columnNumber: 11
                }, this);
            case "tool":
            case "tool_call":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: `text-xs ${textColor}`,
                    children: [
                        "Tool: ",
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                            children: p.tool_name || "unknown"
                        }, void 0, false, {
                            fileName: "[project]/components/TraceStream.tsx",
                            lineNumber: 36,
                            columnNumber: 19
                        }, this),
                        p.input_summary && ` — input: ${JSON.stringify(p.input_summary)}`,
                        " — ",
                        p.success ? "✅ success" : "❌ failed"
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 35,
                    columnNumber: 11
                }, this);
            case "verify_pass":
            case "pass":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: `text-xs ${textColor}`,
                    children: [
                        "✓ Passed: ",
                        p.verification_type || "check",
                        " — ",
                        p.detail || "verified"
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 45,
                    columnNumber: 11
                }, this);
            case "verify_fail":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: `text-xs ${textColor}`,
                    children: [
                        "✗ Failed: ",
                        p.verification_type || "check",
                        " — ",
                        p.detail || "failed",
                        p.retry_count !== undefined && ` (attempt ${p.retry_count})`
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 51,
                    columnNumber: 11
                }, this);
            case "retry":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: `text-xs ${textColor}`,
                    children: [
                        "Retrying — attempt ",
                        p.attempt || "?",
                        "/",
                        p.max_retries || "?",
                        ": ",
                        p.reason || ""
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 58,
                    columnNumber: 11
                }, this);
            case "generate":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: `text-xs ${textColor}`,
                    children: [
                        "Generating artifact: ",
                        p.artifact_type || "file",
                        p.filename && ` → ${p.filename}`
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 64,
                    columnNumber: 11
                }, this);
            case "done":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: `text-xs ${textColor} space-y-1`,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "whitespace-pre-wrap",
                            children: p.summary || "Task complete."
                        }, void 0, false, {
                            fileName: "[project]/components/TraceStream.tsx",
                            lineNumber: 72,
                            columnNumber: 13
                        }, this),
                        p.artifacts && p.artifacts.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "mt-2 space-y-1",
                            children: p.artifacts.map((a, i)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                    className: `text-[11px] px-2 py-1 rounded ${isCardWhite ? "bg-blue-50 text-blue-800" : "bg-blue-900/30 text-blue-300"}`,
                                    children: [
                                        "📄 ",
                                        a.filename,
                                        " (",
                                        a.type,
                                        ")"
                                    ]
                                }, i, true, {
                                    fileName: "[project]/components/TraceStream.tsx",
                                    lineNumber: 76,
                                    columnNumber: 19
                                }, this))
                        }, void 0, false, {
                            fileName: "[project]/components/TraceStream.tsx",
                            lineNumber: 74,
                            columnNumber: 15
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 71,
                    columnNumber: 11
                }, this);
            case "error":
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: "text-xs text-red-400",
                    children: [
                        "Error: ",
                        p.error || "Unknown error"
                    ]
                }, void 0, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 86,
                    columnNumber: 11
                }, this);
            default:
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                    className: `text-xs ${textColor}`,
                    children: JSON.stringify(p)
                }, void 0, false, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 92,
                    columnNumber: 11
                }, this);
        }
    };
    const getStepBadge = (step)=>{
        const s = step.toLowerCase();
        const badges = {
            classify: {
                label: "🧠 CLASSIFY",
                color: isCardWhite ? "bg-purple-100 text-purple-800" : "bg-purple-900/50 text-purple-300"
            },
            plan: {
                label: "📋 PLAN",
                color: isCardWhite ? "bg-slate-800 text-white" : "bg-white text-slate-900"
            },
            tool_call: {
                label: "⚙ TOOL",
                color: isCardWhite ? "bg-amber-100 text-amber-800" : "bg-amber-900/40 text-amber-300"
            },
            verify_pass: {
                label: "✓ PASS",
                color: isCardWhite ? "bg-green-100 text-green-800" : "bg-green-900/40 text-green-300"
            },
            verify_fail: {
                label: "✗ FAIL",
                color: isCardWhite ? "bg-red-100 text-red-800" : "bg-red-900/40 text-red-300"
            },
            retry: {
                label: "🔄 RETRY",
                color: isCardWhite ? "bg-yellow-100 text-yellow-800" : "bg-yellow-900/40 text-yellow-300"
            },
            generate: {
                label: "📄 GENERATE",
                color: isCardWhite ? "bg-blue-100 text-blue-800" : "bg-blue-900/40 text-blue-300"
            },
            done: {
                label: "✅ DONE",
                color: isCardWhite ? "bg-green-100 text-green-800" : "bg-green-900/40 text-green-300"
            },
            error: {
                label: "❌ ERROR",
                color: isCardWhite ? "bg-red-100 text-red-800" : "bg-red-900/40 text-red-300"
            }
        };
        const match = badges[s] || (s.includes("pass") ? badges.verify_pass : s.includes("tool") ? badges.tool_call : null);
        return match || {
            label: step.toUpperCase(),
            color: isCardWhite ? "bg-slate-800 text-white" : "bg-white text-slate-900"
        };
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: `rounded-xl border p-5 shadow-lg font-mono text-xs transition-colors ${isCardWhite ? "bg-white border-gray-200" : "bg-slate-900 border-slate-800"}`,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "space-y-3 max-h-[480px] overflow-y-auto",
            children: events.length === 0 ? /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                className: `${isCardWhite ? "text-gray-400" : "text-zinc-500"} italic`,
                children: "Waiting for agent events..."
            }, void 0, false, {
                fileName: "[project]/components/TraceStream.tsx",
                lineNumber: 126,
                columnNumber: 11
            }, this) : events.map((evt, idx)=>{
                const badge = getStepBadge(evt.step);
                return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                    className: `p-3.5 rounded-lg border flex flex-col gap-1.5 transition-colors ${isCardWhite ? "bg-gray-50 border-gray-200" : "bg-slate-950/70 border-slate-800/80"}`,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex items-center gap-3",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: `font-bold text-[11px] px-2 py-0.5 rounded shadow-sm ${badge.color}`,
                                    children: badge.label
                                }, void 0, false, {
                                    fileName: "[project]/components/TraceStream.tsx",
                                    lineNumber: 142,
                                    columnNumber: 19
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                    className: `text-[11px] font-mono ${isCardWhite ? "text-gray-500" : "text-zinc-400"}`,
                                    children: evt.timestamp
                                }, void 0, false, {
                                    fileName: "[project]/components/TraceStream.tsx",
                                    lineNumber: 147,
                                    columnNumber: 19
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/components/TraceStream.tsx",
                            lineNumber: 141,
                            columnNumber: 17
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "pt-0.5",
                            children: renderDetails(evt)
                        }, void 0, false, {
                            fileName: "[project]/components/TraceStream.tsx",
                            lineNumber: 155,
                            columnNumber: 17
                        }, this)
                    ]
                }, idx, true, {
                    fileName: "[project]/components/TraceStream.tsx",
                    lineNumber: 133,
                    columnNumber: 15
                }, this);
            })
        }, void 0, false, {
            fileName: "[project]/components/TraceStream.tsx",
            lineNumber: 124,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/TraceStream.tsx",
        lineNumber: 117,
        columnNumber: 5
    }, this);
}
_c = TraceStream;
var _c;
__turbopack_context__.k.register(_c, "TraceStream");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/lib/ws-client.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "connectWebSocket",
    ()=>connectWebSocket
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
function connectWebSocket(taskId, onEvent, onError) {
    const wsUrl = __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].env.NEXT_PUBLIC_WS_URL || `ws://localhost:8000/trace/${taskId}`;
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (message)=>{
        try {
            const data = JSON.parse(message.data);
            onEvent(data);
        } catch (err) {
            console.error("JSON parse error:", err);
        }
    };
    if (onError) ws.onerror = onError;
    return ()=>{
        if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
            ws.close();
        }
    };
}
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/node_modules/next/navigation.js [app-client] (ecmascript)", ((__turbopack_context__, module, exports) => {

module.exports = __turbopack_context__.r("[project]/node_modules/next/dist/client/components/navigation.js [app-client] (ecmascript)");
}),
]);

//# sourceMappingURL=_09m_ok-._.js.map