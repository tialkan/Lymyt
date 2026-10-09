import type { Metadata } from "next";
import PortalShell from "@/components/portal/PortalShell";
import LymytClient from "./LymytClient";
import styles from "./lymyt.module.css";

export const metadata: Metadata = {
  title: "Lymyt — Sıfırdan tasarım, devre ve 3D gövde | TezAtlas",
  description: "Nano ESP32 ile kendi masa arkadaşını yap: Codex ve Claude Code limitleri, C1 İngilizce kelimeler, OLED/e-paper seçenekleri, Robotistan örnek sepeti, görsel devre rehberi ve 3D baskı dosyaları.",
  alternates: { canonical: "https://tezatlas.com/lymyt" },
  openGraph: { title: "Lymyt — İki göz. Bir masa arkadaşı.", description: "Sıfırdan tasarım: malzemelerini seç, devreni kur, gövdeni yazdır.", url: "https://tezatlas.com/lymyt", type: "website", siteName: "TezAtlas" },
};

export default function LymytPage() {
  return <PortalShell aktif="lymyt"><div className={styles.page}><LymytClient /></div></PortalShell>;
}
