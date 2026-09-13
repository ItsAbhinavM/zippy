import { Box, Stack, Typography } from "@mui/material";
import CreditCardIcon from "@mui/icons-material/CreditCard";
import { useFinancialStore, emptyArray } from "../../store/useFinancialStore";
import { ItemCard } from "./ItemCard";
import type { PaymentItem } from "../../types/state";

const typeLabel = {
  loan_emi: "Loan EMI",
  credit_card_min: "Card · min due",
  credit_card_full: "Card · full",
};

export function PaymentsCard() {
  const payments = useFinancialStore((s) => s.state?.payments ?? emptyArray<PaymentItem>());
  if (payments.length === 0) return null;

  return (
    <Box>
      <Typography variant="overline" color="text.secondary">Loans & Credit Cards</Typography>
      <Stack direction="row" spacing={1.5} useFlexGap flexWrap="wrap" mt={0.5}>
        {payments.map((p) => (
          <ItemCard
            key={p.id}
            icon={<CreditCardIcon fontSize="small" color="secondary" />}
            title={p.label}
            subtitle={`${typeLabel[p.type]}${p.due_day ? ` · due ${p.due_day}` : ""}`}
            amount={p.amount}
            confidence={p.confidence}
          />
        ))}
      </Stack>
    </Box>
  );
}