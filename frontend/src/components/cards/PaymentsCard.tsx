import { Card, CardContent, Typography, Stack, Chip } from "@mui/material";
import { useFinancialStore, emptyArray } from "../../store/useFinancialStore";

const typeLabel = {
  loan_emi: "Loan EMI",
  credit_card_min: "Credit card (min due)",
  credit_card_full: "Credit card (full)",
};

const confidenceColor = { confirmed: "success", estimated: "warning", uncertain: "error" } as const;

export function PaymentsCard() {
  const payments = useFinancialStore((s) => s.state?.payments ?? emptyArray<PaymentItem>());
  if (payments.length === 0) return null;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Loans & Credit Cards</Typography>
        <Stack spacing={1}>
          {payments.map((p) => (
            <Stack key={p.id} direction="row" justifyContent="space-between" alignItems="center">
              <Typography variant="body2">
                {p.label} · {typeLabel[p.type]}
                {p.due_day ? ` · due ${p.due_day}` : ""}
              </Typography>
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography variant="body2" fontWeight={600}>
                  {p.amount !== null ? `₹${p.amount.toLocaleString()}` : "—"}
                </Typography>
                <Chip size="small" label={p.confidence} color={confidenceColor[p.confidence]} />
              </Stack>
            </Stack>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}