import { useEffect, useState } from "react";
import { api, type Item } from "../api";

interface Props {
  selectedId: number | null;
  onSelect: (id: number) => void;
}

export function ItemList({ selectedId, onSelect }: Props) {
  const [items, setItems] = useState<Item[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listItems().then(setItems, (e: Error) => setError(e.message));
  }, []);

  if (error) return <p role="alert">Couldn't load items: {error}</p>;
  if (items === null) return <p aria-busy="true">Loading items…</p>;
  if (items.length === 0) return <p>No items yet.</p>;

  return (
    <nav aria-label="Items">
      <ul className="item-list">
        {items.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              className="item-button"
              aria-current={item.id === selectedId ? "true" : undefined}
              onClick={() => onSelect(item.id)}
            >
              <span>{item.title}</span>
              <span className={item.available ? "badge badge-ok" : "badge badge-busy"}>
                {item.available ? "Available" : "On loan"}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
