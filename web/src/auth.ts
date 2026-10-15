// The company SSO login page stores the access token here after sign-in.
const TOKEN_KEY = "shelf.accessToken";

export function getAccessToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}
