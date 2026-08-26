package com.nsu.mspagent;

import android.content.Context;
import android.content.SharedPreferences;

public final class AppConfig {
    private static final String PREFS = "msp_agent_config";
    private final SharedPreferences p;
    public AppConfig(Context c) { p = c.getSharedPreferences(PREFS, Context.MODE_PRIVATE); }

    public boolean cloudFirst() { return p.getBoolean("cloud_first", true); }
    public String cloudBaseUrl() { return p.getString("cloud_base_url", "https://api.openai.com/v1"); }
    public String cloudApiKey() { return p.getString("cloud_api_key", ""); }
    public String cloudFastModel() { return p.getString("cloud_model_fast", "gpt-4o-mini"); }
    public String cloudDeepModel() { return p.getString("cloud_model_deep", "gpt-4o"); }
    public String cloudCodeModel() { return p.getString("cloud_model_code", "gpt-4o"); }
    public String cloudDocModel() { return p.getString("cloud_model_doc", "gpt-4o-mini"); }
    public String cloudResearchModel() { return p.getString("cloud_model_research", "gpt-4o-mini"); }
    public String cloudVisionModel() { return p.getString("cloud_model_vision", "gpt-4o-mini"); }

    public String ollamaUrl() { return p.getString("ollama_url", "http://192.168.1.10:11434"); }
    public String searxUrl() { return p.getString("searx_url", "http://192.168.1.10:8080"); }
    public String fastModel() { return p.getString("model_fast", "llama3.2:3b"); }
    public String deepModel() { return p.getString("model_deep", "qwen2.5:7b"); }
    public String codeModel() { return p.getString("model_code", "qwen2.5-coder:7b"); }
    public String docModel() { return p.getString("model_doc", "llama3.2:3b"); }
    public String researchModel() { return p.getString("model_research", "llama3.2:3b"); }
    public String visionModel() { return p.getString("model_vision", "llama3.2-vision"); }
    public boolean onlineFirst() { return p.getBoolean("online_first", false); }

    public void save(boolean cloudFirst, String cloudBaseUrl, String cloudApiKey,
                      String cloudFast, String cloudDeep, String cloudCode, String cloudDoc, String cloudResearch, String cloudVision,
                      String ollama, String searx, String fast, String deep, String code, String doc, String research, String vision,
                      boolean onlineFirst) {
        p.edit()
            .putBoolean("cloud_first", cloudFirst)
            .putString("cloud_base_url", trim(cloudBaseUrl))
            .putString("cloud_api_key", cloudApiKey == null ? "" : cloudApiKey.trim())
            .putString("cloud_model_fast", trim(cloudFast)).putString("cloud_model_deep", trim(cloudDeep))
            .putString("cloud_model_code", trim(cloudCode)).putString("cloud_model_doc", trim(cloudDoc))
            .putString("cloud_model_research", trim(cloudResearch)).putString("cloud_model_vision", trim(cloudVision))
            .putString("ollama_url", trim(ollama)).putString("searx_url", trim(searx))
            .putString("model_fast", trim(fast)).putString("model_deep", trim(deep))
            .putString("model_code", trim(code)).putString("model_doc", trim(doc))
            .putString("model_research", trim(research)).putString("model_vision", trim(vision))
            .putBoolean("online_first", onlineFirst).apply();
    }
    private static String trim(String s) { return s == null ? "" : s.trim().replaceAll("/+$", ""); }
}
