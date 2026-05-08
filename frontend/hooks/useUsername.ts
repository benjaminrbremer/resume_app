"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export function useUsername(): string | null {
  const router = useRouter();
  const [username, setUsernameState] = useState<string | null>(null);

  useEffect(() => {
    const u = localStorage.getItem("username");
    if (!u) {
      router.replace("/login");
    } else {
      setUsernameState(u);
    }
  }, [router]);

  return username;
}
