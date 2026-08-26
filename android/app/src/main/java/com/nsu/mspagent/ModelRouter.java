package com.nsu.mspagent;

public final class ModelRouter {
    public static String chooseRole(String text) {
        String t = text == null ? "" : text.toLowerCase();
        if (contains(t, "image", "screenshot", "picture")) return "vision";
        if (contains(t, "powershell", "script", "ps1", "bash", "function", "compile", "automation", "code")) return "code";
        if (contains(t, "document", "pdf", "docx", "xlsx", "pptx", "ocr", "file")) return "doc";
        if (contains(t, "latest", "current", "recent", "vendor docs", "official docs", "cve", "release notes", "research")) return "research";
        if (contains(t, "root cause", "deep", "analyze", "logs", "architecture", "complex", "troubleshoot")) return "deep";
        return "fast";
    }
    public static boolean shouldResearch(String text) {
        String t = text == null ? "" : text.toLowerCase();
        return contains(t, "latest", "current", "recent", "vendor docs", "official docs", "cve", "release notes", "look up", "research", "verify online");
    }
    private static boolean contains(String s, String... terms) { for (String x : terms) if (s.contains(x)) return true; return false; }
}
