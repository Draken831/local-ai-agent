package com.nsu.mspagent;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.*;

public final class KnowledgeStore {
    private final SharedPreferences p;
    public KnowledgeStore(Context c) { p=c.getSharedPreferences("knowledge", Context.MODE_PRIVATE); }
    public JSONArray all() { try { return new JSONArray(p.getString("items","[]")); } catch(Exception e){ return new JSONArray(); } }
    public void add(String title,String keywords,String body) { JSONArray a=all(); a.put(new JSONObject().put("title",title).put("keywords",keywords).put("body",body)); p.edit().putString("items",a.toString()).apply(); }
    public void clear(){ p.edit().remove("items").apply(); }
    public String context(String q){ String t=q==null?"":q.toLowerCase(); JSONArray a=all(); StringBuilder s=new StringBuilder(); for(int i=0;i<a.length();i++){ JSONObject x=a.optJSONObject(i); if(x==null)continue; String keys=x.optString("keywords").toLowerCase(); for(String k:keys.split(",")){ if(!k.trim().isEmpty()&&t.contains(k.trim())){ s.append("LOCAL KNOWLEDGE: ").append(x.optString("title")).append("\n").append(x.optString("body")).append("\n\n"); break; } } } return s.toString(); }
}
