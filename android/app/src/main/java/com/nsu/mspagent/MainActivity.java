package com.nsu.mspagent;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.*;

public class MainActivity extends Activity {
    @Override public void onCreate(Bundle b){ super.onCreate(b); LinearLayout p=Ui.page(this,"MSP AI Agent — Cloud First");
        p.addView(Ui.text(this,"Android client for the MSP AI Agent. Chat, research, document and image requests go to your configured cloud API first, automatically falling back to your local Ollama host if the cloud is unreachable. Configure both under Connection &amp; Model Settings."));
        add(p,"Agent Chat",ChatActivity.class); add(p,"Native System Controls",SystemControlsActivity.class); add(p,"Document Analysis",DocumentActivity.class); add(p,"Vision / Screenshot Analysis",VisionActivity.class); add(p,"Local Knowledge",KnowledgeActivity.class); add(p,"Connection & Model Settings",SettingsActivity.class);
        setContentView(Ui.scroll(this,p)); }
    private void add(LinearLayout p,String t,Class<?> c){ Button x=Ui.button(this,t); x.setOnClickListener(v->startActivity(new Intent(this,c))); p.addView(x); }
}
