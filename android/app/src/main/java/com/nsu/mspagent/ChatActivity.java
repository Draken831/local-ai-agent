package com.nsu.mspagent;

import android.app.Activity;
import android.os.Bundle;
import android.widget.*;
import java.util.concurrent.*;

public class ChatActivity extends Activity {
    private TextView out;
    private EditText input;
    private final ExecutorService ex = Executors.newSingleThreadExecutor();

    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        LinearLayout p = Ui.page(this, "Agent Chat");
        out = new TextView(this);
        out.setTextSize(15);
        out.setText("Ready. Cloud is the normal first provider; local paths are fallback or explicit.\n");
        out.setTextIsSelectable(true);
        p.addView(out, new LinearLayout.LayoutParams(-1, 0, 1));

        input = Ui.input(this, "Ask an MSP / infrastructure question");
        p.addView(input);

        LinearLayout actions = new LinearLayout(this);
        actions.setOrientation(LinearLayout.HORIZONTAL);

        Button send = Ui.button(this, "Send Cloud-First");
        send.setOnClickListener(v -> send());
        actions.addView(send, new LinearLayout.LayoutParams(0, -2, 1));

        Button quick = Ui.button(this, "Local Quick");
        quick.setOnClickListener(v -> localQuick());
        actions.addView(quick, new LinearLayout.LayoutParams(0, -2, 1));

        p.addView(actions);
        setContentView(p);
    }

    private void send() {
        String q = input.getText().toString().trim();
        if (q.isEmpty()) return;
        input.setText("");
        out.append("\nYou: " + q + "\n");

        ex.submit(() -> {
            try {
                AppConfig c = new AppConfig(this);
                String role = ModelRouter.chooseRole(q);
                StringBuilder prompt = new StringBuilder();

                String k = new KnowledgeStore(this).context(q);
                if (!k.isEmpty()) prompt.append(k);

                if (c.onlineFirst() && ModelRouter.shouldResearch(q)) {
                    try {
                        prompt.append(SearxClient.context(c.searxUrl(), q, 5));
                    } catch (Exception e) {
                        prompt.append("LOCAL RESEARCH FAILED: ").append(e.getMessage()).append("\n");
                    }
                }

                prompt.append("USER REQUEST:\n").append(q);

                String system =
                    "You are an MSP-focused AI agent. Use the configured cloud provider first and local inference only as fallback. " +
                    "Prefer precise, safe, actionable technical guidance. Flag destructive actions and require explicit confirmation before destructive changes.";

                HybridClient hc = new HybridClient(c);
                String ans = hc.chat(role, system, prompt.toString());
                append("\nAgent [" + hc.lastUsed() + "]:\n" + ans + "\n");
            } catch (Exception e) {
                append("\nERROR: " + e.getMessage() + "\n");
            }
        });
    }

    private void localQuick() {
        String q = input.getText().toString().trim();
        if (q.isEmpty()) {
            Toast.makeText(this, "Enter a question first.", Toast.LENGTH_SHORT).show();
            return;
        }
        String quick = new QuickAnswerStore(this).match(q);
        if (quick == null) {
            append("\nLocal Quick: no matching answer.\n");
        } else {
            append("\nAgent [local quick answer]:\n" + quick + "\n");
        }
    }

    private void append(String s) {
        runOnUiThread(() -> out.append(s));
    }

    @Override protected void onDestroy() {
        ex.shutdownNow();
        super.onDestroy();
    }
}
