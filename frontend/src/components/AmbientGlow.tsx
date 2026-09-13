import { Box } from "@mui/material";
import type { AgentAudioState } from "../hooks/useAgentAudioState";

const COLOR_MAP: Record<AgentAudioState, string> = {
  idle: "rgba(243,239,230,0.16)",
  processing: "rgba(217,142,62,0.42)",   // warm amber — user's turn being processed
  replying: "rgba(76,154,106,0.46)",     // green — assistant responding
};

const HEIGHT_MAP: Record<AgentAudioState, string> = {
  idle: "16%",
  processing: "34%",
  replying: "38%",
};

export function AmbientGlow({ state }: { state: AgentAudioState }) {
  return (
    <Box
      aria-hidden
      sx={{
        position: "absolute",
        bottom: 0,
        left: "50%",
        transform: "translateX(-50%)",
        width: "160%",
        height: HEIGHT_MAP[state],
        borderRadius: "50% 50% 0 0",
        background: `radial-gradient(ellipse at bottom, ${COLOR_MAP[state]} 0%, transparent 72%)`,
        filter: "blur(28px)",
        transition: "height 700ms ease, background 700ms ease",
        pointerEvents: "none",
        zIndex: 0,
      }}
    />
  );
}