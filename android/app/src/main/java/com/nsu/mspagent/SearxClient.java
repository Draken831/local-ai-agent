package com.nsu.mspagent;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import org.json.*;

public final class SearxClient {
    public static String context(String base, String query, int max) throws Exception {
        if (base == null || base.trim().isEmpty()) return "";
        String url = base.replaceAll("/+$", "") + "/search?q=" + URLEncoder.encode(query, StandardCharsets.UTF_8.name()) + "&format=json";
        JSONObject j = new JSONObject(HttpUtil.get(url, 30000)); JSONArray a = j.optJSONArray("results");
        StringBuilder out = new StringBuilder("ONLINE RESEARCH CONTEXT\nQuery: ").append(query).append("\n\n");
        if (a != null) for (int i=0; i<Math.min(max, a.length()); i++) {
            JSONObject x = a.optJSONObject(i); if (x == null) continue;
            out.append("Result ").append(i+1).append(": ").append(x.optString("title")).append("\nURL: ")
               .append(x.optString("url")).append("\nSnippet: ").append(x.optString("content")).append("\n\n");
        }
        return out.toString();
    }
}
