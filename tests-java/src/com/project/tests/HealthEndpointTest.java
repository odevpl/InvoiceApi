package com.project.tests;

import org.junit.jupiter.api.Test;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class HealthEndpointTest {

    @Test
    public void testHealthEndpoint() throws IOException {

        // URL of the /health endpoint
        URL url = new URL("http://127.0.0.1:8000/health");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.connect();

        int responseCode = conn.getResponseCode();
        assertEquals(200, responseCode, "Check if the /health endpoint returns HTTP 200");

        // Read JSON response
        Scanner scanner = new Scanner(url.openStream());
        StringBuilder response = new StringBuilder();
        while (scanner.hasNext()) {
            response.append(scanner.nextLine());
        }
        scanner.close();

        // Verify the content of the response
        String expected = "{\"status\":\"ok\"}";
        assertEquals(expected, response.toString(), "Check the content of the /health response");
    }
}