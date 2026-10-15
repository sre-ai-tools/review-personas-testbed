import { useEffect, useState } from "react";
import { api, type Item } from "../api";
import { BorrowForm } from "./BorrowForm";

export function ItemDetail({ itemId }: { itemId: number }) {
  const [item, setItem] = useState<Item | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getItem(itemId).then(setItem, (e: Error) => setError(e.message));
  }, [itemId]);

  if (error) return <p role="alert">Couldn't load this item: {error}</p>;
  if (item === null) return <p aria-busy="true">Loading…</p>;

  return (
    <section aria-labelledby="item-title" className="item-detail">
      <h2 id="item-title">{item.title}</h2>
      <dl>
        <dt>Type</dt>
        <dd>{item.kind === "book" ? "Book" : "Equipment"}</dd>
        <dt>Owner</dt>
        <dd>{item.owner_email}</dd>
      </dl>
      {item.available ? (
        <BorrowForm itemId={item.id} onBorrowed={() => setItem({ ...item, available: false })} />
      ) : (
        <p>This item is on loan.</p>
      )}
    </section>
  );
}
