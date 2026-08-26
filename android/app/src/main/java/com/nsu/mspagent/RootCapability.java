package com.nsu.mspagent;

import java.io.*;

public final class RootCapability {
    public static boolean available() {
        try { Process p=new ProcessBuilder("su","-c","id").redirectErrorStream(true).start(); return p.waitFor()==0; } catch(Exception e){ return false; }
    }
    public static String runSafe(String action) throws Exception {
        String cmd;
        switch(action){
            case "animationsOff": cmd="settings put global window_animation_scale 0; settings put global transition_animation_scale 0; settings put global animator_duration_scale 0"; break;
            case "animationsHalf": cmd="settings put global window_animation_scale 0.5; settings put global transition_animation_scale 0.5; settings put global animator_duration_scale 0.5"; break;
            case "animationsNormal": cmd="settings put global window_animation_scale 1; settings put global transition_animation_scale 1; settings put global animator_duration_scale 1"; break;
            case "getenforce": cmd="getenforce"; break;
            default: throw new SecurityException("Action is not in the privileged allow-list.");
        }
        Process p=new ProcessBuilder("su","-c",cmd).redirectErrorStream(true).start(); BufferedReader br=new BufferedReader(new InputStreamReader(p.getInputStream())); StringBuilder s=new StringBuilder(); String l; while((l=br.readLine())!=null)s.append(l).append('\n'); int code=p.waitFor(); if(code!=0)throw new IOException("su exited "+code+": "+s); return s.toString().trim();
    }
}
