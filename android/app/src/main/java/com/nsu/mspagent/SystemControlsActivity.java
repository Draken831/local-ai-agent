package com.nsu.mspagent;

import android.app.*;
import android.app.admin.DevicePolicyManager;
import android.content.*;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.*;

public class SystemControlsActivity extends Activity {
    private LinearLayout p; private DevicePolicyManager dpm; private ComponentName admin;
    @Override public void onCreate(Bundle b){ super.onCreate(b); p=Ui.page(this,"Native System Controls"); dpm=(DevicePolicyManager)getSystemService(DEVICE_POLICY_SERVICE); admin=new ComponentName(this,AdminReceiver.class);
        p.addView(Ui.text(this,"Control tiers are permission-aware. Normal controls use supported Android APIs; managed controls require Device Admin/Device Owner; privileged controls appear only when root already exists. No arbitrary root shell is exposed."));
        Button grant=Ui.button(this,"Grant Modify System Settings"); grant.setOnClickListener(v->startActivity(new Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS, Uri.parse("package:"+getPackageName())))); p.addView(grant);
        p.addView(Ui.text(this,"Screen brightness")); SeekBar br=new SeekBar(this); br.setMax(255); try{br.setProgress(Settings.System.getInt(getContentResolver(),Settings.System.SCREEN_BRIGHTNESS));}catch(Exception ignored){} br.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){ public void onProgressChanged(SeekBar s,int val,boolean user){ if(user&&Settings.System.canWrite(SystemControlsActivity.this)) Settings.System.putInt(getContentResolver(),Settings.System.SCREEN_BRIGHTNESS,Math.max(1,val)); } public void onStartTrackingTouch(SeekBar s){} public void onStopTrackingTouch(SeekBar s){} }); p.addView(br);
        Spinner timeout=new Spinner(this); String[] labels={"30 seconds","1 minute","2 minutes","5 minutes","10 minutes","30 minutes"}; int[] vals={30000,60000,120000,300000,600000,1800000}; timeout.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,labels)); p.addView(timeout); Button setTimeout=Ui.button(this,"Apply Screen Timeout"); setTimeout.setOnClickListener(v->{ if(!Settings.System.canWrite(this)){Toast.makeText(this,"Grant Modify System Settings first",Toast.LENGTH_LONG).show();return;} Settings.System.putInt(getContentResolver(),Settings.System.SCREEN_OFF_TIMEOUT,vals[timeout.getSelectedItemPosition()]); Toast.makeText(this,"Applied",Toast.LENGTH_SHORT).show();}); p.addView(setTimeout);
        addSettingsButton("Open Wi-Fi panel",Settings.Panel.ACTION_WIFI); addSettingsButton("Open Internet panel",Settings.Panel.ACTION_INTERNET_CONNECTIVITY); addSettingsButton("Open app notification settings",Settings.ACTION_APP_NOTIFICATION_SETTINGS);
        Button adminBtn=Ui.button(this,"Activate Device Admin"); adminBtn.setOnClickListener(v->{ Intent i=new Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN); i.putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN,admin); i.putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION,"Enables locally initiated management actions such as Lock Now."); startActivity(i);}); p.addView(adminBtn);
        Button lock=Ui.button(this,"Lock Device Now"); lock.setOnClickListener(v->{ if(dpm.isAdminActive(admin)) new AlertDialog.Builder(this).setTitle("Lock device?").setMessage("This immediately locks the device.").setNegativeButton("Cancel",null).setPositiveButton("Lock",(d,w)->dpm.lockNow()).show(); else Toast.makeText(this,"Activate Device Admin first",Toast.LENGTH_LONG).show();}); p.addView(lock);
        boolean owner=dpm.isDeviceOwnerApp(getPackageName()); p.addView(Ui.text(this,"Device Owner status: "+(owner?"ACTIVE":"Not provisioned")+". Device Owner is the supported Android Enterprise path for deeper managed-device control."));
        boolean root=RootCapability.available(); p.addView(Ui.text(this,"Root status: "+(root?"available":"not available")+". Privileged actions remain allow-listed and require a local tap.")); if(root){ addRoot("Set animation scales to 0.5x","animationsHalf"); addRoot("Restore animation scales to 1x","animationsNormal"); Button se=Ui.button(this,"Read SELinux mode"); se.setOnClickListener(v->rootAction("getenforce",false)); p.addView(se); }
        setContentView(Ui.scroll(this,p)); }
    private void addSettingsButton(String label,String action){ Button b=Ui.button(this,label); b.setOnClickListener(v->{ Intent i=new Intent(action); if(action.equals(Settings.ACTION_APP_NOTIFICATION_SETTINGS)) i.putExtra(Settings.EXTRA_APP_PACKAGE,getPackageName()); startActivity(i);}); p.addView(b); }
    private void addRoot(String label,String action){ Button b=Ui.button(this,label); b.setOnClickListener(v->rootAction(action,true)); p.addView(b); }
    private void rootAction(String action,boolean confirm){ Runnable r=()->new Thread(()->{ try{ String o=RootCapability.runSafe(action); runOnUiThread(()->Toast.makeText(this,o.isEmpty()?"Applied":o,Toast.LENGTH_LONG).show()); }catch(Exception e){runOnUiThread(()->Toast.makeText(this,"Privileged action failed: "+e.getMessage(),Toast.LENGTH_LONG).show());}}).start(); if(confirm)new AlertDialog.Builder(this).setTitle("Apply privileged change?").setMessage("This uses existing root access and changes a system setting.").setNegativeButton("Cancel",null).setPositiveButton("Apply",(d,w)->r.run()).show();else r.run(); }
}
