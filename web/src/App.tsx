import { useState } from "react";
import { ItemList } from "./components/ItemList";
import { ItemDetail } from "./components/ItemDetail";

export function App() {
  const [selectedId, setSelectedId] = useState<number | null>(null);

  return (
    <>
      <header className="site-header">
        <h1>Shelf</h1>
        <p>Borrow books and equipment from your team.</p>
      </header>
      <main className="layout">
        <ItemList selectedId={selectedId} onSelect={setSelectedId} />
        {selectedId !== null && <ItemDetail key={selectedId} itemId={selectedId} />}
      </main>
    </>
  );
}
