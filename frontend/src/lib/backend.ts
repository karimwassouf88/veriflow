import { cookies } from "next/headers";

const FASTAPI_URL = process.env.FASTAPI_URL ?? "http://localhost:8000";

export async function backendFetch(path: string, options: RequestInit = {}) {
  const cookieStore = await cookies();
  const token = cookieStore.get("veriflow_access_token")?.value;

  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type") &&
    options.body
  ) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(`${FASTAPI_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });
}
