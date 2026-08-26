package com.nsu.mspagent;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.Map;

public final class HttpUtil {
    public static String postJson(String url, String json, int timeoutMs) throws Exception {
        return postJson(url, json, timeoutMs, null);
    }
    public static String postJson(String url, String json, int timeoutMs, Map<String,String> headers) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(timeoutMs); c.setReadTimeout(timeoutMs); c.setRequestMethod("POST");
        c.setDoOutput(true); c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
        if (headers != null) for (Map.Entry<String,String> e : headers.entrySet()) c.setRequestProperty(e.getKey(), e.getValue());
        try (OutputStream os = c.getOutputStream()) { os.write(json.getBytes(StandardCharsets.UTF_8)); }
        return read(c);
    }
    public static String get(String url, int timeoutMs) throws Exception {
        return get(url, timeoutMs, null);
    }
    public static String get(String url, int timeoutMs, Map<String,String> headers) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(timeoutMs); c.setReadTimeout(timeoutMs); c.setRequestMethod("GET");
        c.setRequestProperty("User-Agent", "msp-local-agent-android/1.0");
        if (headers != null) for (Map.Entry<String,String> e : headers.entrySet()) c.setRequestProperty(e.getKey(), e.getValue());
        return read(c);
    }
    private static String read(HttpURLConnection c) throws Exception {
        int code = c.getResponseCode(); InputStream in = code >= 200 && code < 300 ? c.getInputStream() : c.getErrorStream();
        StringBuilder sb = new StringBuilder(); try (BufferedReader br = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
            String line; while ((line = br.readLine()) != null) sb.append(line).append('\n');
        }
        if (code < 200 || code >= 300) throw new IOException("HTTP " + code + ": " + sb);
        return sb.toString();
    }
}
