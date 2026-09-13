import { Card, CardContent, Typography, Stack } from "@mui/material";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import { useFinancialStore, emptyArray } from "../../store/useFinancialStore";
import type { MissingField } from "../../types/state";

export function MissingInfoCard() {
  const missing = useFinancialStore((s) => s.state?.missing_fields ?? emptyArray<MissingField>());
  if (missing.length === 0) return null;

  return (
    <Card sx={{ borderLeft: "4px solid", borderColor: "warning.main" }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Still Missing</Typography>
        <Stack spacing={1.5}>
          {missing.map((m) => (
            <Stack key={m.id} direction="row" spacing={1} alignItems="flex-start">
              <InfoOutlinedIcon fontSize="small" color="warning" sx={{ mt: "2px" }} />
              <Stack>
                <Typography variant="body2">{m.description}</Typography>
                <Typography variant="caption" color="text.secondary">{m.why_it_matters}</Typography>
              </Stack>
            </Stack>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}