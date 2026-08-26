package com.nsu.mspagent;

import android.content.Context;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;

public final class QuickAnswerStore {
    private final Context context;
    public QuickAnswerStore(Context c) { context = c; }
    private String asset() throws Exception {
        try (InputStream in = context.getAssets().open("quick_answers.json")) {
            ByteArrayOutputStream o = new ByteArrayOutputStream(); byte[] b = new byte[4096]; int n;
            while ((n=in.read(b))>0) o.write(b,0,n); return o.toString(StandardCharsets.UTF_8.name());
        }
    }
    public String match(String q) {
        try {
            String t = norm(q); JSONArray a = new JSONArray(asset());
            for (int i=0;i<a.length();i++) {
                JSONObject x=a.getJSONObject(i); JSONArray groups=x.optJSONArray("match_all_groups"); boolean ok=groups!=null && groups.length()>0;
                if (groups != null) for (int g=0; g<groups.length(); g++) { JSONArray group=groups.optJSONArray(g); boolean any=false;
                    if (group != null) for (int k=0;k<group.length();k++) if (t.contains(norm(group.optString(k)))) { any=true; break; }
                    if (!any) { ok=false; break; }
                }
                if (ok) { JSONArray lines=x.optJSONArray("answer_lines"); StringBuilder s=new StringBuilder(); if(lines!=null) for(int k=0;k<lines.length();k++) s.append(lines.optString(k)).append('\n'); return s.toString().trim(); }
            }
        } catch (Exception ignored) {}
        return null;
    }
    private static String norm(String s) { return (s==null?"":s.toLowerCase()).replace("microsfot","microsoft").replace("owershell","powershell").replaceAll("\\s+"," ").trim(); }
}
