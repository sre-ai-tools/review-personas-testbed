import { useState, type FormEvent } from "react";
import { api } from "../api";

interface Props {
  itemId: number;
  onBorrowed: () => void;
}

export function BorrowForm({ itemId, onBorrowed }: Props) {
  const [days, setDays] = useState(14);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.borrow(itemId, days);
      onBorrowed();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={submit} className="borrow-form">
      <label htmlFor="borrow-days">Borrow for (days)</label>
      <input
        id="borrow-days"
        type="number"
        min={1}
        max={60}
        value={days}
        onChange={(e) => setDays(Number(e.target.value))}
        aria-describedby="borrow-days-hint"
      />
      <p id="borrow-days-hint" className="hint">
        Up to 60 days. Late returns cost 50¢ a day.
      </p>
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? "Borrowing…" : "Borrow"}
      </button>
    </form>
  );
}
