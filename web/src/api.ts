// Typed client for the Shelf API. Keep these types in step with api/app/models.py.
import { getAccessToken } from "./auth";

export type Kind = "book" | "equipment";

export interface Item {
  id: number;
  title: string;
  kind: Kind;
  owner_email: string;
  available: boolean;
  created_at: string;
  photo_url: string | null;
}

export type PhotoType = "image/jpeg" | "image/png" | "image/webp";

export interface PhotoUpload {
  url: string;
  fields: Record<string, string>;
}

export interface Loan {
  id: number;
  item_id: number;
  borrower_email: string;
  borrowed_at: string;
  due_at: string;
  returned_at: string | null;
  late_fee_cents: number | null;
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

// FastAPI sends `detail` as a string, or as a list of field errors for a 422.
function errorMessage(detail: unknown): string | null {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d: { msg?: string }) => d.msg ?? "Invalid request").join("; ");
  }
  return null;
}

const BASE_URL = import.meta.env.VITE_API_URL as string;

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(token ? { authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, errorMessage(body.detail) ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listItems: (limit = 50, offset = 0) => request<Item[]>(`/items?limit=${limit}&offset=${offset}`),
  getItem: (id: number) => request<Item>(`/items/${id}`),
  borrow: (itemId: number, days: number) =>
    request<Loan>("/loans", { method: "POST", body: JSON.stringify({ item_id: itemId, days }) }),
  returnItem: (loanId: number) => request<Loan>(`/loans/${loanId}/return`, { method: "POST" }),
  overdue: () => request<Loan[]>("/loans/overdue"),
  requestPhotoUpload: (itemId: number, contentType: PhotoType) =>
    request<PhotoUpload>(`/items/${itemId}/photo`, {
      method: "POST",
      body: JSON.stringify({ content_type: contentType }),
    }),
};

// Sends the file straight to S3 with the presigned POST from the API.
export async function uploadPhoto(upload: PhotoUpload, file: File): Promise<void> {
  const form = new FormData();
  Object.entries(upload.fields).forEach(([key, value]) => form.append(key, value));
  form.append("file", file);
  const res = await fetch(upload.url, { method: "POST", body: form });
  if (!res.ok) throw new ApiError(res.status, "Upload failed");
}
