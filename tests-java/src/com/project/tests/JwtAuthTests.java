package com.project.tests;

import org.junit.jupiter.api.Test;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Instant;
import java.util.Base64;

import static org.junit.jupiter.api.Assertions.*;

class JwtAuthTests {

    private static final String baseUrl = "http://127.0.0.1:8000";
    private static final String username = "user";
    private static final String password = "password";


    @Test
    void accessTokenShouldExpireWithin15Minutes() throws Exception {
        String accessToken = getAccessToken();

        String payload = decodePayload(accessToken);
        long exp = extractExp(payload);
        long now = Instant.now().getEpochSecond();

        assertTrue(exp - now <= 900);
    }

    @Test
    void protectedEndpointShouldReturnUserData() throws Exception {
        String accessToken = getAccessToken();

        HttpURLConnection conn = (HttpURLConnection)
                new URL(baseUrl + "/protected").openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Authorization", "Bearer " + accessToken);

        assertEquals(200, conn.getResponseCode());

        String body = readBody(conn);
        assertTrue(body.contains(username));
        assertTrue(body.contains("role"));
    }

    @Test
    void protectedEndpointWithoutTokenShouldReturn401() throws Exception {
        HttpURLConnection conn = (HttpURLConnection)
                new URL(baseUrl + "/protected").openConnection();
        conn.setRequestMethod("GET");

        assertEquals(401, conn.getResponseCode());
    }

    @Test
    void protectedEndpointWithInvalidTokenShouldReturn401() throws Exception {
        HttpURLConnection conn = (HttpURLConnection)
                new URL(baseUrl + "/protected").openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Authorization", "Bearer invalid.token.value");

        assertEquals(401, conn.getResponseCode());
    }




    private HttpURLConnection login() throws Exception {
        HttpURLConnection conn = (HttpURLConnection)
                new URL(baseUrl + "/auth/login").openConnection();
        conn.setRequestMethod("POST");
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");

        String body = "username=" + username + "&password=" + password;
        try (OutputStream os = conn.getOutputStream()) {
            os.write(body.getBytes());
        }
        return conn;
    }

    private String getAccessToken() throws Exception {
        String response = readBody(login());
        return extractValue(response, "access_token");
    }

    private String[] getTokens() throws Exception {
        String response = readBody(login());
        return new String[]{
                extractValue(response, "access_token"),
                extractValue(response, "refresh_token")
        };
    }

    private HttpURLConnection refresh(String refreshToken) throws Exception {
        HttpURLConnection conn = (HttpURLConnection)
                new URL(baseUrl + "/auth/refresh").openConnection();
        conn.setRequestMethod("POST");
        conn.setDoOutput(true);
        conn.setRequestProperty("Content-Type", "application/json");

        String body = "{\"refresh_token\":\"" + refreshToken + "\"}";
        try (OutputStream os = conn.getOutputStream()) {
            os.write(body.getBytes());
        }
        return conn;
    }

    private String readBody(HttpURLConnection conn) throws Exception {
        InputStream is = conn.getResponseCode() >= 400
                ? conn.getErrorStream()
                : conn.getInputStream();

        return new BufferedReader(new InputStreamReader(is))
                .lines().reduce("", String::concat);
    }

    private String extractValue(String json, String key) {
        return json.split("\"" + key + "\":\"")[1].split("\"")[0];
    }

    private String decodePayload(String jwt) {
        return new String(Base64.getUrlDecoder().decode(jwt.split("\\.")[1]));
    }

    private long extractExp(String payload) {
        return Long.parseLong(payload.split("\"exp\":")[1].split("[,}]")[0]);
    }
}
