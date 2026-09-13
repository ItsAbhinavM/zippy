import { Box, Stack, Typography } from "@mui/material";
import HomeIcon from "@mui/icons-material/Home";
import LocalMallIcon from "@mui/icons-material/LocalMall";
import { useFinancialStore, emptyArray } from "../../store/useFinancialStore";
import { ItemCard } from "./ItemCard";
import type { ExpenseItem } from "../../types/state";

export function ExpensesCard() {
  const essentials = useFinancialStore((s) => s.state?.essential_expenses ?? emptyArray<ExpenseItem>());
  const optional = useFinancialStore((s) => s.state?.optional_expenses ?? emptyArray<ExpenseItem>());

  if (essentials.length === 0 && optional.length === 0) return null;

  return (
    <Stack spacing={2}>
      {essentials.length > 0 && (
        <Box>
          <Typography variant="overline" color="text.secondary">Essential Expenses</Typography>
          <Stack direction="row" spacing={1.5} useFlexGap flexWrap="wrap" mt={0.5}>
            {essentials.map((e) => (
              <ItemCard
                key={e.id}
                icon={<HomeIcon fontSize="small" color="action" />}
                title={e.label}
                subtitle={e.day_of_month ? `Day ${e.day_of_month}` : undefined}
                amount={e.amount}
                confidence={e.confidence}
              />
            ))}
          </Stack>
        </Box>
      )}
      {optional.length > 0 && (
        <Box>
          <Typography variant="overline" color="text.secondary">Optional Expenses</Typography>
          <Stack direction="row" spacing={1.5} useFlexGap flexWrap="wrap" mt={0.5}>
            {optional.map((e) => (
              <ItemCard
                key={e.id}
                icon={<LocalMallIcon fontSize="small" color="action" />}
                title={e.label}
                subtitle={e.day_of_month ? `Day ${e.day_of_month}` : undefined}
                amount={e.amount}
                confidence={e.confidence}
              />
            ))}
          </Stack>
        </Box>
      )}
    </Stack>
  );
}