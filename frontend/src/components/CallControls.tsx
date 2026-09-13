import { Button, Stack, Chip } from "@mui/material";
import MicIcon from "@mui/icons-material/Mic";
import MicOffIcon from "@mui/icons-material/MicOff";
import CallEndIcon from "@mui/icons-material/CallEnd";
import { useDaily, useLocalSessionId, useAudioTrack } from "@daily-co/daily-react";
import { useFinancialStore } from "../store/useFinancialStore";

export function CallControls({ onEnd }: { onEnd: () => void }) {
  const daily = useDaily();
  const localSessionId = useLocalSessionId();
  const localAudio = useAudioTrack(localSessionId);
  const connected = useFinancialStore((s) => s.connected);

  // isOff reflects Daily's actual track state — safer than a separate
  // useState that could drift out of sync with the real call state
  const muted = localAudio?.isOff ?? false;

  const toggleMute = () => {
    if (!daily) return;
    daily.setLocalAudio(muted); // if currently off, this turns it back on
  };

  return (
    <Stack direction="row" spacing={2} alignItems="center">
      <Chip
        size="small"
        label={connected ? "Live" : "Connecting"}
        color={connected ? "success" : "default"}
      />
      <Button
        variant="outlined"
        startIcon={muted ? <MicOffIcon /> : <MicIcon />}
        onClick={toggleMute}
      >
        {muted ? "Unmute" : "Mute"}
      </Button>
      <Button
        variant="contained"
        color="error"
        startIcon={<CallEndIcon />}
        onClick={onEnd}
      >
        End conversation
      </Button>
    </Stack>
  );
}