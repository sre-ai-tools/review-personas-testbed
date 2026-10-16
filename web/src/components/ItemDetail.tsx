import { useEffect, useState } from "react";
import { api, type Item } from "../api";
import { BorrowForm } from "./BorrowForm";
import { PhotoUploader } from "./PhotoUploader";

interface Props {
  itemId: number;
  onChanged: () => void;
}

export function ItemDetail({ itemId, onChanged }: Props) {
  const [item, setItem] = useState<Item | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    api.getItem(itemId).then(
      (result) => !ignore && setItem(result),
      (e: Error) => !ignore && setError(e.message),
    );
    return () => {
      ignore = true;
    };
  }, [itemId]);

  if (error) return <p role="alert">Couldn't load this item: {error}</p>;
  if (item === null) return <p aria-busy="true">Loading…</p>;

  return (
    <section aria-labelledby="item-title" className="item-detail">
      <h2 id="item-title">{item.title}</h2>
      {item.photo_url && (
        <img className="item-photo" src={item.photo_url} alt={`Photo of ${item.title}`} />
      )}
      <dl>
        <dt>Type</dt>
        <dd>{item.kind === "book" ? "Book" : "Equipment"}</dd>
        <dt>Owner</dt>
        <dd>{item.owner_email}</dd>
      </dl>
      {item.available ? (
        <BorrowForm
          itemId={item.id}
          onBorrowed={() => {
            setItem({ ...item, available: false });
            onChanged();
          }}
        />
      ) : (
        <p>This item is on loan.</p>
      )}
      <PhotoUploader itemId={item.id} onUploaded={() => api.getItem(itemId).then(setItem)} />
    </section>
  );
}
