import { Card, CardContent, Typography, Stack, Chip, Divider } from "@mui/material";
import { useFinancialStore, emptyArray } from "../../store/useFinancialStore";
import type { ExpenseItem } from "../../types/state";

const confidenceColor = { confirmed: "success", estimated: "warning", uncertain: "error" } as const;

function Row({ item }: { item: ExpenseItem }) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="center">
      <Typography variant="body2">
        {item.label}{item.day_of_month ? ` · day ${item.day_of_month}` : ""}
      </Typography>
      <Stack direction="row" spacing={1} alignItems="center">
        <Typography variant="body2" fontWeight={600}>
          {item.amount !== null ? `₹${item.amount.toLocaleString()}` : "—"}
        </Typography>
        <Chip size="small" label={item.confidence} color={confidenceColor[item.confidence]} />
      </Stack>
    </Stack>
  );
}

export function ExpensesCard() {
  const essentials = useFinancialStore((s) => s.state?.essential_expenses ?? emptyArray<ExpenseItem>());
  const optional = useFinancialStore((s) => s.state?.optional_expenses ?? emptyArray<ExpenseItem>());

  if (essentials.length === 0 && optional.length === 0) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Expenses</Typography>

        {essentials.length > 0 && (
          <>
            <Typography variant="overline" color="text.secondary">Essential</Typography>
            <Stack spacing={1} mb={2}>
              {essentials.map((e) => <Row key={e.id} item={e} />)}
            </Stack>
          </>
        )}

        {essentials.length > 0 && optional.length > 0 && <Divider sx={{ mb: 2 }} />}

        {optional.length > 0 && (
          <>
            <Typography variant="overline" color="text.secondary">Optional</Typography>
            <Stack spacing={1}>
              {optional.map((e) => <Row key={e.id} item={e} />)}
            </Stack>
          </>
        )}
      </CardContent>
    </Card>
  );
}