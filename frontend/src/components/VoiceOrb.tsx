import { Box, Typography } from "@mui/material";
import { useRemoteParticipants, useTracks, useTrackVolume, type TrackReference } from "@livekit/components-react";
import { Track } from "livekit-client";

export function VoiceOrb() {
  const remoteParticipants = useRemoteParticipants();
  const bot = remoteParticipants[0];

  const audioTracks = useTracks([
    {
      source: Track.Source.Microphone,
      withPlaceholder: false,
    },
  ]);

  const botAudioTrack = audioTracks.find(
    (track): track is TrackReference =>
      track.participant.identity === bot?.identity &&
      track.publication !== undefined
  );

  const level = useTrackVolume(botAudioTrack);

  const scale = 1 + Math.min(level ?? 0, 1) * 0.4;

  return (
    <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
      <Box
        sx={{
          width: 72,
          height: 72,
          borderRadius: "50%",
          bgcolor: "primary.main",
          transform: `scale(${scale})`,
          transition: "transform 80ms ease-out",
          opacity: bot ? 1 : 0.4,
        }}
      />
      <Typography variant="caption" color="text.secondary">
        {bot ? "Assistant is on the call" : "Connecting…"}
      </Typography>
    </Box>
  );
}