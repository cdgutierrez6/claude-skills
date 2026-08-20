# Postman Collection — Template JSON mínimo

```json
{
  "info": {
    "name": "EfiziAI CRM API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{ "key": "token", "value": "{{jwt_token}}" }]
  },
  "variable": [
    { "key": "base_url", "value": "http://localhost:3001/v1" },
    { "key": "jwt_token", "value": "" }
  ],
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "event": [{
            "listen": "test",
            "script": {
              "exec": ["pm.environment.set('jwt_token', pm.response.json().token);"]
            }
          }],
          "request": {
            "method": "POST",
            "url": "{{base_url}}/auth/login",
            "body": {
              "mode": "raw",
              "raw": "{\"email\":\"admin@test.com\",\"password\":\"password\"}",
              "options": { "raw": { "language": "json" } }
            }
          }
        }
      ]
    }
  ]
}
```
