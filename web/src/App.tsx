import { useState } from "react";
import { ItemList } from "./components/ItemList";
import { ItemDetail } from "./components/ItemDetail";

export function App() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  // Bumped when an item changes, so the list re-fetches its availability.
  const [listVersion, setListVersion] = useState(0);

  return (
    <>
      <header className="site-header">
        <h1>Shelf</h1>
        <p>Borrow books and equipment from your team.</p>
      </header>
      <main className="layout">
        <ItemList selectedId={selectedId} onSelect={setSelectedId} version={listVersion} />
        {selectedId !== null && <ItemDetail
            key={selectedId}
            itemId={selectedId}
            onChanged={() => setListVersion((v) => v + 1)}
          />}
      </main>
    </>
  );
}
