import { Box, Stack, Typography } from "@mui/material";
import PaidIcon from "@mui/icons-material/Paid";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import { useFinancialStore, emptyArray } from "../../store/useFinancialStore";
import { ItemCard } from "./ItemCard";
import type { IncomeItem } from "../../types/state";

export function IncomeCard() {
  const income = useFinancialStore((s) => s.state?.income ?? emptyArray<IncomeItem>());
  const startingBalance = useFinancialStore((s) => s.state?.starting_balance ?? null);

  if (income.length === 0 && startingBalance === null) return null;

  return (
    <Box>
      <Typography variant="overline" color="text.secondary">Income</Typography>
      <Stack direction="row" spacing={1.5} useFlexGap flexWrap="wrap" mt={0.5}>
        {startingBalance !== null && (
          <ItemCard
            icon={<AccountBalanceWalletIcon fontSize="small" color="primary" />}
            title="Available now"
            amount={startingBalance}
            confidence="confirmed"
          />
        )}
        {income.map((item) => (
          <ItemCard
            key={item.id}
            icon={<PaidIcon fontSize="small" color="primary" />}
            title={item.label}
            subtitle={item.day_of_month ? `Day ${item.day_of_month}` : "Date unknown"}
            amount={item.amount}
            confidence={item.confidence}
          />
        ))}
      </Stack>
    </Box>
  );
}