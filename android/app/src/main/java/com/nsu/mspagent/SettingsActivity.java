package com.nsu.mspagent;

import android.app.Activity;
import android.os.Bundle;
import android.widget.*;

public class SettingsActivity extends Activity {
    @Override public void onCreate(Bundle b){ super.onCreate(b); AppConfig c=new AppConfig(this); LinearLayout p=Ui.page(this,"Connection & Models");

        p.addView(Ui.text(this,"Cloud (tried first)"));
        CheckBox cloudFirst=new CheckBox(this); cloudFirst.setText("Cloud-first (fall back to local Ollama if unreachable)"); cloudFirst.setChecked(c.cloudFirst()); p.addView(cloudFirst);
        EditText cloudBase=Ui.input(this,"Cloud API base URL (OpenAI-compatible)"); cloudBase.setText(c.cloudBaseUrl()); p.addView(cloudBase);
        EditText cloudKey=Ui.input(this,"Cloud API key"); cloudKey.setText(c.cloudApiKey()); p.addView(cloudKey);
        EditText cFast=Ui.input(this,"Cloud fast model"); cFast.setText(c.cloudFastModel()); p.addView(cFast);
        EditText cDeep=Ui.input(this,"Cloud deep model"); cDeep.setText(c.cloudDeepModel()); p.addView(cDeep);
        EditText cCode=Ui.input(this,"Cloud code model"); cCode.setText(c.cloudCodeModel()); p.addView(cCode);
        EditText cDoc=Ui.input(this,"Cloud document model"); cDoc.setText(c.cloudDocModel()); p.addView(cDoc);
        EditText cResearch=Ui.input(this,"Cloud research model"); cResearch.setText(c.cloudResearchModel()); p.addView(cResearch);
        EditText cVision=Ui.input(this,"Cloud vision model"); cVision.setText(c.cloudVisionModel()); p.addView(cVision);
        Button testCloud=Ui.button(this,"Test cloud connection"); testCloud.setOnClickListener(v->new Thread(()->{ try{ new CloudClient(cloudBase.getText().toString(),cloudKey.getText().toString()).health(); runOnUiThread(()->Toast.makeText(this,"Cloud reachable",Toast.LENGTH_LONG).show()); }catch(Exception e){ runOnUiThread(()->Toast.makeText(this,"Cloud connection failed: "+e.getMessage(),Toast.LENGTH_LONG).show()); }}).start()); p.addView(testCloud);

        p.addView(Ui.text(this,"Local fallback (Ollama)"));
        EditText oll=Ui.input(this,"Ollama base URL"); oll.setText(c.ollamaUrl()); p.addView(oll);
        EditText sea=Ui.input(this,"SearXNG base URL"); sea.setText(c.searxUrl()); p.addView(sea);
        EditText fast=Ui.input(this,"Local fast model"); fast.setText(c.fastModel()); p.addView(fast);
        EditText deep=Ui.input(this,"Local deep model"); deep.setText(c.deepModel()); p.addView(deep);
        EditText code=Ui.input(this,"Local code model"); code.setText(c.codeModel()); p.addView(code);
        EditText doc=Ui.input(this,"Local document model"); doc.setText(c.docModel()); p.addView(doc);
        EditText research=Ui.input(this,"Local research model"); research.setText(c.researchModel()); p.addView(research);
        EditText vision=Ui.input(this,"Local vision model"); vision.setText(c.visionModel()); p.addView(vision);
        CheckBox online=new CheckBox(this); online.setText("Use local SearXNG context before cloud for research queries (optional)"); online.setChecked(c.onlineFirst()); p.addView(online);
        Button testOllama=Ui.button(this,"Test Ollama connection"); testOllama.setOnClickListener(v->new Thread(()->{ try{ new OllamaClient(oll.getText().toString()).health(); runOnUiThread(()->Toast.makeText(this,"Ollama reachable",Toast.LENGTH_LONG).show()); }catch(Exception e){ runOnUiThread(()->Toast.makeText(this,"Connection failed: "+e.getMessage(),Toast.LENGTH_LONG).show()); }}).start()); p.addView(testOllama);

        Button save=Ui.button(this,"Save"); save.setOnClickListener(v->{
            c.save(cloudFirst.isChecked(),cloudBase.getText().toString(),cloudKey.getText().toString(),
                cFast.getText().toString(),cDeep.getText().toString(),cCode.getText().toString(),cDoc.getText().toString(),cResearch.getText().toString(),cVision.getText().toString(),
                oll.getText().toString(),sea.getText().toString(),fast.getText().toString(),deep.getText().toString(),code.getText().toString(),doc.getText().toString(),research.getText().toString(),vision.getText().toString(),
                online.isChecked());
            Toast.makeText(this,"Saved",Toast.LENGTH_SHORT).show();
        }); p.addView(save);
        setContentView(Ui.scroll(this,p)); }
}
