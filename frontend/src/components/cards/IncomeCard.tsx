import { Card, CardContent, Typography, Stack, Chip } from "@mui/material";
import { useFinancialStore, emptyArray } from "../../store/useFinancialStore";
import type { IncomeItem } from "../../types/state";

const confidenceColor = { confirmed: "success", estimated: "warning", uncertain: "error" } as const;

export function IncomeCard() {
  const income = useFinancialStore((s) => s.state?.income ?? emptyArray<IncomeItem>());
  const startingBalance = useFinancialStore((s) => s.state?.starting_balance ?? null);

  if (income.length === 0 && startingBalance === null) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Income</Typography>
        {startingBalance !== null && (
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Available right now: ₹{startingBalance.toLocaleString()}
          </Typography>
        )}
        <Stack spacing={1}>
          {income.map((item) => (
            <Stack key={item.id} sx={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", }} >
              <Typography variant="body2">
                {item.label}
                {item.day_of_month ? ` · day ${item.day_of_month}` : " · date unknown"}
              </Typography>
              <Stack sx={{ flexDirection: "row", gap: 1, alignItems: "center", }}>
                <Typography variant="body2" fontWeight={600}>
                  {item.amount !== null ? `₹${item.amount.toLocaleString()}` : "—"}
                </Typography>
                <Chip size="small" label={item.confidence} color={confidenceColor[item.confidence]} />
              </Stack>
            </Stack>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}