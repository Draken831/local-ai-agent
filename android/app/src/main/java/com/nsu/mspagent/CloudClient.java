package com.nsu.mspagent;

import org.json.JSONArray;
import org.json.JSONObject;
import java.util.HashMap;
import java.util.Map;

/**
 * OpenAI-compatible cloud LLM client. Works unmodified with any provider
 * that speaks the standard /chat/completions schema (OpenAI, Azure OpenAI,
 * OpenRouter, Groq, Together, etc.) - change the base URL / API key in
 * Settings to switch provider.
 */
public final class CloudClient {
    private final String base; private final String apiKey;
    public CloudClient(String base, String apiKey) {
        this.base = (base == null ? "" : base.trim()).replaceAll("/+$", "");
        this.apiKey = apiKey;
        if (!this.base.toLowerCase().startsWith("https://")) {
            throw new IllegalArgumentException("Cloud API base URL must use HTTPS.");
        }
    }

    public boolean hasKey() { return apiKey != null && !apiKey.trim().isEmpty(); }

    private Map<String,String> headers() {
        Map<String,String> h = new HashMap<>();
        if (hasKey()) h.put("Authorization", "Bearer " + apiKey.trim());
        return h;
    }

    public String chat(String model, String system, String user) throws Exception {
        JSONObject body = new JSONObject(); body.put("model", model); body.put("temperature", 0.2); body.put("max_tokens", 900);
        JSONArray messages = new JSONArray();
        messages.put(new JSONObject().put("role", "system").put("content", system));
        messages.put(new JSONObject().put("role", "user").put("content", user));
        body.put("messages", messages);
        JSONObject r = new JSONObject(HttpUtil.postJson(base + "/chat/completions", body.toString(), 15000, headers()));
        return extractContent(r);
    }

    public String vision(String model, String prompt, String base64, String mimeType) throws Exception {
        JSONArray content = new JSONArray();
        content.put(new JSONObject().put("type", "text").put("text", prompt));
        content.put(new JSONObject().put("type", "image_url").put("image_url",
            new JSONObject().put("url", "data:" + mimeType + ";base64," + base64)));
        JSONObject body = new JSONObject().put("model", model).put("temperature", 0.1).put("max_tokens", 900);
        JSONArray messages = new JSONArray().put(new JSONObject().put("role", "user").put("content", content));
        body.put("messages", messages);
        JSONObject r = new JSONObject(HttpUtil.postJson(base + "/chat/completions", body.toString(), 15000, headers()));
        return extractContent(r);
    }

    private static String extractContent(JSONObject r) {
        JSONArray choices = r.optJSONArray("choices");
        if (choices == null || choices.length() == 0) return "No response.";
        JSONObject message = choices.optJSONObject(0) == null ? null : choices.optJSONObject(0).optJSONObject("message");
        return message == null ? "No response." : message.optString("content", "").trim();
    }

    public String health() throws Exception { return HttpUtil.get(base + "/models", 5000, headers()); }
}
