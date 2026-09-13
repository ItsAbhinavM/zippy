import { DailyProvider, useDaily } from "@daily-co/daily-react";
import { useEffect,type ReactNode } from "react";

function JoinOnMount({ url, token }: { url: string; token: string }) {
  const daily = useDaily();

  useEffect(() => {
    if (!daily) return;
    daily.join({ url, token });
    return () => {
      daily.leave();
    };
  }, [daily, url, token]);

  return null;
}

export function CallProvider({
  url,
  token,
  children,
}: {
  url: string;
  token: string;
  children: ReactNode;
}) {
  return (
    <DailyProvider>
      <JoinOnMount url={url} token={token} />
      {children}
    </DailyProvider>
  );
}