export type GuestScanItem = {
  mode: "url" | "qr" | "file";
  title: string;
  score: number;
  verdict: string;
  scanned_at: string;
};

const KEY = "cga_guest_scans";
const MAX = 20;

export function loadGuestHistory(): GuestScanItem[] {
  try {
    const raw = sessionStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as GuestScanItem[];
    return Array.isArray(parsed) ? parsed.slice(0, MAX) : [];
  } catch {
    return [];
  }
}

export function pushGuestScan(item: GuestScanItem): GuestScanItem[] {
  const next = [item, ...loadGuestHistory().filter((x) => x.title !== item.title)].slice(0, MAX);
  sessionStorage.setItem(KEY, JSON.stringify(next));
  return next;
}

export function clearGuestHistory(): void {
  sessionStorage.removeItem(KEY);
}
