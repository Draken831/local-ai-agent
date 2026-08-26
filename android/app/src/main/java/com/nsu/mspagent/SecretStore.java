package com.nsu.mspagent;

import android.content.Context;
import android.content.SharedPreferences;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;

import java.nio.charset.StandardCharsets;
import java.security.KeyStore;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** Stores the cloud API key encrypted with an Android Keystore AES key. */
public final class SecretStore {
    private static final String PREFS = "msp_agent_secrets";
    private static final String ALIAS = "msp_agent_cloud_api_key_v1";
    private static final String ENC_KEY = "cloud_api_key_enc";
    private static final String IV_KEY = "cloud_api_key_iv";

    private final SharedPreferences p;

    public SecretStore(Context context) {
        p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    private SecretKey key() throws Exception {
        KeyStore ks = KeyStore.getInstance("AndroidKeyStore");
        ks.load(null);
        if (!ks.containsAlias(ALIAS)) {
            KeyGenerator kg = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
            kg.init(new KeyGenParameterSpec.Builder(
                    ALIAS,
                    KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .build());
            kg.generateKey();
        }
        return ((KeyStore.SecretKeyEntry) ks.getEntry(ALIAS, null)).getSecretKey();
    }

    public void set(String value) {
        try {
            String text = value == null ? "" : value.trim();
            if (text.isEmpty()) {
                clear();
                return;
            }
            Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
            c.init(Cipher.ENCRYPT_MODE, key());
            byte[] encrypted = c.doFinal(text.getBytes(StandardCharsets.UTF_8));
            p.edit()
                    .putString(ENC_KEY, Base64.encodeToString(encrypted, Base64.NO_WRAP))
                    .putString(IV_KEY, Base64.encodeToString(c.getIV(), Base64.NO_WRAP))
                    .apply();
        } catch (Exception e) {
            throw new IllegalStateException("Could not securely store cloud API key.", e);
        }
    }

    public String get() {
        try {
            String enc = p.getString(ENC_KEY, "");
            String iv = p.getString(IV_KEY, "");
            if (enc == null || enc.isEmpty() || iv == null || iv.isEmpty()) return "";
            Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
            c.init(Cipher.DECRYPT_MODE, key(), new GCMParameterSpec(128, Base64.decode(iv, Base64.NO_WRAP)));
            byte[] plain = c.doFinal(Base64.decode(enc, Base64.NO_WRAP));
            return new String(plain, StandardCharsets.UTF_8);
        } catch (Exception e) {
            return "";
        }
    }

    public boolean hasValue() { return !get().isEmpty(); }

    public void clear() {
        p.edit().remove(ENC_KEY).remove(IV_KEY).apply();
    }
}
