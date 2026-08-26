package com.nsu.mspagent;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;

public final class OllamaClient {
    private static final int READ_TIMEOUT_MS = 600000;
    private static final int CONNECT_TIMEOUT_MS = 10000;
    private static final String KEEP_ALIVE = "30m";

    private final String base;
    public OllamaClient(String base) { this.base = base.replaceAll("/+$", ""); }

    public String chat(String model, String system, String user) throws Exception {
        JSONObject body = new JSONObject(); body.put("model", model); body.put("stream", true); body.put("keep_alive", KEEP_ALIVE);
        JSONArray messages = new JSONArray();
        messages.put(new JSONObject().put("role", "system").put("content", system));
        messages.put(new JSONObject().put("role", "user").put("content", user));
        body.put("messages", messages); body.put("options", new JSONObject().put("temperature", 0.2).put("num_predict", 900));
        return streamChat(body);
    }

    public String vision(String model, String prompt, String base64) throws Exception {
        JSONObject body = new JSONObject().put("model", model).put("stream", true).put("keep_alive", KEEP_ALIVE);
        JSONArray images = new JSONArray().put(base64);
        JSONArray messages = new JSONArray().put(new JSONObject().put("role", "user").put("content", prompt).put("images", images));
        body.put("messages", messages).put("options", new JSONObject().put("temperature", 0.1).put("num_predict", 900));
        return streamChat(body);
    }

    private String streamChat(JSONObject body) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(base + "/api/chat").openConnection();
        c.setConnectTimeout(CONNECT_TIMEOUT_MS); c.setReadTimeout(READ_TIMEOUT_MS); c.setRequestMethod("POST");
        c.setDoOutput(true); c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
        try (OutputStream os = c.getOutputStream()) { os.write(body.toString().getBytes(StandardCharsets.UTF_8)); }
        int code = c.getResponseCode();
        InputStream in = code >= 200 && code < 300 ? c.getInputStream() : c.getErrorStream();
        StringBuilder content = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (line.trim().isEmpty()) continue;
                if (code < 200 || code >= 300) { content.append(line).append('\n'); continue; }
                try {
                    JSONObject obj = new JSONObject(line);
                    JSONObject msg = obj.optJSONObject("message");
                    if (msg != null) content.append(msg.optString("content", ""));
                    if (obj.optBoolean("done", false)) break;
                } catch (Exception ignore) { }
            }
        }
        if (code < 200 || code >= 300) throw new IOException("HTTP " + code + ": " + content);
        String result = content.toString().trim();
        return result.isEmpty() ? "No response." : result;
    }

    public String health() throws Exception { return HttpUtil.get(base + "/api/tags", 8000); }
}
