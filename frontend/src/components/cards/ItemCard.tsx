import { Grow, Paper, Stack, Typography, Chip } from "@mui/material";
import type { ReactNode } from "react";

const confidenceColor = { confirmed: "success", estimated: "warning", uncertain: "error" } as const;

export function ItemCard({
  icon,
  title,
  subtitle,
  amount,
  confidence,
}: {
  icon: ReactNode;
  title: string;
  subtitle?: string;
  amount: number | null;
  confidence: "confirmed" | "estimated" | "uncertain";
}) {
  return (
    <Grow in appear>
      <Paper
        elevation={1}
        sx={{
          p: 1.5,
          minWidth: 180,
          borderTop: "3px solid",
          borderColor: `${confidenceColor[confidence]}.main`,
        }}
      >
        <Stack direction="row" spacing={1} alignItems="center" mb={0.5}>
          {icon}
          <Typography variant="subtitle2" noWrap>{title}</Typography>
        </Stack>
        {subtitle && (
          <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
            {subtitle}
          </Typography>
        )}
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" fontWeight={700}>
            {amount !== null ? `₹${amount.toLocaleString()}` : "—"}
          </Typography>
          <Chip size="small" label={confidence} color={confidenceColor[confidence]} />
        </Stack>
      </Paper>
    </Grow>
  );
}