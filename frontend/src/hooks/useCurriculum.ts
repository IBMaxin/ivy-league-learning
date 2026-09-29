import { useEffect, useState } from "react";
import { api, type Track } from "../api/client";

// Data concern: curriculum loading. No rendering logic beyond state.
export function useCurriculum() {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    api
      .curriculum()
      .then((d) => setTracks(d.tracks))
      .catch(() => setError("Backend offline — showing starter content."));
  }, []);
  return { tracks, error };
}
