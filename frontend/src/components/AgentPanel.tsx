import { Box } from "@mui/material";
import { VoiceOrb } from "./VoiceOrb";
import { LiveCaption } from "./LiveCaptions";
import { CallControls } from "./CallControls";

export function AgentPanel({ onEnd }: { onEnd: () => void }) {
  return (
    <Box
      sx={{
        position: "sticky",
        top: 24,
        bgcolor: "background.paper",
        borderRadius: 4,
        border: "1px solid",
        borderColor: "divider",
        p: 3,
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <VoiceOrb />
      <LiveCaption />
      <CallControls onEnd={onEnd} />
    </Box>
  );
}