import { useState, type FormEvent } from "react";
import { api, uploadPhoto, type PhotoType } from "../api";

const ACCEPTED: PhotoType[] = ["image/jpeg", "image/png", "image/webp"];
const MAX_BYTES = 5 * 1024 * 1024;

interface Props {
  itemId: number;
  onUploaded: () => void;
}

export function PhotoUploader({ itemId, onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    if (!ACCEPTED.includes(file.type as PhotoType)) {
      setStatus("Choose a JPEG, PNG or WebP image.");
      return;
    }
    if (file.size > MAX_BYTES) {
      setStatus("Photos can be up to 5 MB.");
      return;
    }
    setBusy(true);
    setStatus("Uploading…");
    try {
      const upload = await api.requestPhotoUpload(itemId, file.type as PhotoType);
      await uploadPhoto(upload, file);
      setStatus("Photo updated.");
      onUploaded();
    } catch (e) {
      setStatus(`Upload failed: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="photo-uploader">
      <label htmlFor="item-photo">Item photo</label>
      <input
        id="item-photo"
        type="file"
        accept={ACCEPTED.join(",")}
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <button type="submit" disabled={!file || busy}>
        Upload photo
      </button>
      <p role="status">{status}</p>
    </form>
  );
}
