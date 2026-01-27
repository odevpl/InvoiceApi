package com.project.tests;

import org.junit.jupiter.api.Test;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class UserRegistrationTests {

    private final String baseUrl = "http://localhost:8000/auth/register";

    private HttpURLConnection sendPostRequest(String json) throws Exception {
        URL url = new URL(baseUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setDoOutput(true);

        try (OutputStream os = conn.getOutputStream()) {
            os.write(json.getBytes());
            os.flush();
        }

        return conn;
    }

    @Test
    void testSuccessfulRegistration() throws Exception {
        String username = "user_" + UUID.randomUUID();
        String email = "patrycjakilian1+" + UUID.randomUUID() + "@gmail.com";
        String json = String.format("""
                {
                    "username": "%s",
                    "email": "%s",
                    "password": "Password123",
                    "confirm_password": "Password123"
                }
                """, username, email);

        HttpURLConnection conn = sendPostRequest(json);
        assertEquals(201, conn.getResponseCode());
    }

    @Test
    void testMissingEmail() throws Exception {
        String username = "user_" + UUID.randomUUID();
        String json = String.format("""
                {
                    "username": "%s",
                    "password": "Password123",
                    "confirm_password": "Password123"
                }
                """, username);

        HttpURLConnection conn = sendPostRequest(json);
        assertEquals(422, conn.getResponseCode()); // FastAPI zwraca 422
    }

    @Test
    void testPasswordMismatch() throws Exception {
        String username = "user_" + UUID.randomUUID();
        String email = "patrycjakilian1+" + UUID.randomUUID() + "@gmail.com";
        String json = String.format("""
                {
                    "username": "%s",
                    "email": "%s",
                    "password": "Password123",
                    "confirm_password": "Password124"
                }
                """, username, email);

        HttpURLConnection conn = sendPostRequest(json);
        assertEquals(400, conn.getResponseCode());
    }

    @Test
    void testMissingUsername() throws Exception {
        String email = "patrycjakilian1+" + UUID.randomUUID() + "@gmail.com";
        String json = String.format("""
                {
                    "email": "%s",
                    "password": "Password123",
                    "confirm_password": "Password123"
                }
                """, email);

        HttpURLConnection conn = sendPostRequest(json);
        assertEquals(422, conn.getResponseCode());
    }

    @Test
    void testShortPassword() throws Exception {
        String username = "user_" + UUID.randomUUID();
        String email = "patrycjakilian1+" + UUID.randomUUID() + "@gmail.com";
        String json = String.format("""
                {
                    "username": "%s",
                    "email": "%s",
                    "password": "short",
                    "confirm_password": "short"
                }
                """, username, email);

        HttpURLConnection conn = sendPostRequest(json);
        assertEquals(422, conn.getResponseCode());
    }
}
