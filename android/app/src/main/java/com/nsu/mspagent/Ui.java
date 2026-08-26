package com.nsu.mspagent;

import android.content.Context;
import android.graphics.Color;
import android.view.ViewGroup;
import android.widget.*;

public final class Ui {
    public static LinearLayout page(Context c,String title){ LinearLayout l=new LinearLayout(c); l.setOrientation(LinearLayout.VERTICAL); l.setPadding(dp(c,18),dp(c,18),dp(c,18),dp(c,18)); TextView t=new TextView(c); t.setText(title); t.setTextSize(24); t.setTextColor(Color.BLACK); t.setPadding(0,0,0,dp(c,14)); l.addView(t,new LinearLayout.LayoutParams(-1,-2)); return l; }
    public static Button button(Context c,String text){ Button b=new Button(c); b.setText(text); b.setAllCaps(false); b.setMinHeight(dp(c,52)); b.setLayoutParams(new LinearLayout.LayoutParams(-1,-2)); return b; }
    public static EditText input(Context c,String hint){ EditText e=new EditText(c); e.setHint(hint); e.setSingleLine(true); e.setLayoutParams(new LinearLayout.LayoutParams(-1,-2)); return e; }
    public static TextView text(Context c,String text){ TextView v=new TextView(c); v.setText(text); v.setTextSize(15); v.setTextColor(Color.DKGRAY); v.setPadding(0,dp(c,8),0,dp(c,8)); return v; }
    public static int dp(Context c,int v){ return Math.round(v*c.getResources().getDisplayMetrics().density); }
    public static ScrollView scroll(Context c, LinearLayout content){ ScrollView s=new ScrollView(c); s.addView(content,new ViewGroup.LayoutParams(-1,-2)); return s; }
}
