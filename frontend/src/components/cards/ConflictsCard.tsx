import { useMemo } from "react";
import { Card, CardContent, Typography, Stack } from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import { useFinancialStore } from "../../store/useFinancialStore";

export function ConflictsCard() {
    const allConflicts = useFinancialStore((s) => s.state?.conflicts)
    const conflicts = useMemo(
        ()=> (allConflicts??[]).filter((c) => !c.resolved),
        [allConflicts]
    );
//   const conflicts = useFinancialStore((s) => (s.state?.conflicts ?? []).filter((c) => !c.resolved));
  if (conflicts.length === 0) return null;

  return (
    <Card sx={{ borderLeft: "4px solid", borderColor: "error.main" }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Needs Clarification</Typography>
        <Stack spacing={1.5}>
          {conflicts.map((c) => (
            <Stack key={c.id} direction="row" spacing={1} alignItems="flex-start">
              <WarningAmberIcon fontSize="small" color="error" sx={{ mt: "2px" }} />
              <Typography variant="body2">
                Two different amounts were mentioned for the same {c.entity_type}:
                {" "}₹{c.values_seen[0]?.toLocaleString()} vs ₹{c.values_seen[1]?.toLocaleString()}.
              </Typography>
            </Stack>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}