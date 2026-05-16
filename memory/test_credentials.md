# Test Credentials

Verified working credentials as of 2026-04-24:

- **Admin**: `support@arabshopping.org` / `Hadi1247@`
- **Seller**: `testseller@test.com` / `TestPass123!`
- **Buyer**: `testbuyer@test.com` / `TestPass123!`

## Notes for testing agents
- Use the isolated Supabase client fix: logins and refresh calls now use per-request clients, so concurrent/sequential user logins no longer invalidate each other's refresh tokens.
- `POST /api/auth/refresh` takes `{refresh_token: str}` — returns `{success, session: {access_token, refresh_token, expires_in, expires_at}}`.
