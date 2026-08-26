package com.nsu.mspagent;

public final class HybridClient {
    private final AppConfig c;
    private volatile String lastUsed = "local";

    public HybridClient(AppConfig c) { this.c = c; }

    public String lastUsed() { return lastUsed; }

    private boolean cloudActive() {
        return c.cloudFirst() && new CloudClient(c.cloudBaseUrl(), c.cloudApiKey()).hasKey();
    }

    public String chat(String role, String system, String user) throws Exception {
        String cloudModel = cloudModelForRole(role);
        String localModel = localModelForRole(role);
        if (cloudActive()) {
            try {
                String out = new CloudClient(c.cloudBaseUrl(), c.cloudApiKey()).chat(cloudModel, system, user);
                lastUsed = "cloud:" + cloudModel;
                return out;
            } catch (Exception e) {
                lastUsed = "local:" + localModel + " (cloud failed: " + e.getMessage() + ")";
                return new OllamaClient(c.ollamaUrl()).chat(localModel, system, user);
            }
        }
        lastUsed = "local:" + localModel;
        return new OllamaClient(c.ollamaUrl()).chat(localModel, system, user);
    }

    public String vision(String prompt, String base64, String mimeType) throws Exception {
        String cloudModel = c.cloudVisionModel();
        String localModel = c.visionModel();
        if (cloudActive()) {
            try {
                String out = new CloudClient(c.cloudBaseUrl(), c.cloudApiKey()).vision(cloudModel, prompt, base64, mimeType);
                lastUsed = "cloud:" + cloudModel;
                return out;
            } catch (Exception e) {
                lastUsed = "local:" + localModel + " (cloud failed: " + e.getMessage() + ")";
                return new OllamaClient(c.ollamaUrl()).vision(localModel, prompt, base64);
            }
        }
        lastUsed = "local:" + localModel;
        return new OllamaClient(c.ollamaUrl()).vision(localModel, prompt, base64);
    }

    private String cloudModelForRole(String role) {
        switch (role) {
            case "deep": return c.cloudDeepModel();
            case "code": return c.cloudCodeModel();
            case "doc": return c.cloudDocModel();
            case "research": return c.cloudResearchModel();
            default: return c.cloudFastModel();
        }
    }

    private String localModelForRole(String role) {
        switch (role) {
            case "deep": return c.deepModel();
            case "code": return c.codeModel();
            case "doc": return c.docModel();
            case "research": return c.researchModel();
            default: return c.fastModel();
        }
    }
}
