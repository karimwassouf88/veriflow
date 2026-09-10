import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.delete("veriflow_access_token");
  response.cookies.delete("veriflow_refresh_token");
  return response;
}
