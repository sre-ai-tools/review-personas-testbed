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
    throw new ApiError(res.status, body.detail ?? res.statusText);
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
};
