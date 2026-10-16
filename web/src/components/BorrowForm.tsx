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
    if (!Number.isInteger(days) || days < 1 || days > 60) {
      setError("Choose between 1 and 60 days.");
      return;
    }
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
      <div className="quick-picks">
        {[7, 14, 28].map((d) => (
          <div
            key={d}
            className={d === days ? "quick-pick selected" : "quick-pick"}
            onClick={() => setDays(d)}
          >
            {d / 7} wk
          </div>
        ))}
      </div>
      <input
        type="number"
        min={1}
        max={60}
        value={days}
        placeholder="Days"
        onChange={(e) => setDays(Number(e.target.value))}
      />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={submitting}>
        {submitting ? "Borrowing…" : "Borrow"}
      </button>
    </form>
  );
}
