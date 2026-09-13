import { Stack, Paper, Typography, Box } from "@mui/material";
import InsightsIcon from "@mui/icons-material/Insights";
import { ConflictsCard } from "./ConflictsCard";
import { MissingInfoCard } from "./MissingInfoCard";
import { IncomeCard } from "./IncomeCard";
import { PaymentsCard } from "./PaymentsCard";
import { ExpensesCard } from "./ExpensesCard";
import { PlanCard } from "./PlanCard";
import { useFinancialStore } from "../../store/useFinancialStore";

function EmptyState() {
  return (
    <Paper
      variant="outlined"
      sx={{
        p: 4,
        borderStyle: "dashed",
        borderColor: "divider",
        textAlign: "center",
        bgcolor: "transparent",
      }}
    >
      <InsightsIcon sx={{ fontSize: 32, color: "text.secondary", mb: 1 }} />
      <Typography variant="body2" color="text.secondary">
        As you talk, your income, expenses, loans, and plan will show up here.
      </Typography>
    </Paper>
  );
}

export function CardGrid() {
  const hasAnything = useFinancialStore((s) => {
    const st = s.state;
    if (!st) return false;
    return (
      st.income.length > 0 ||
      st.essential_expenses.length > 0 ||
      st.optional_expenses.length > 0 ||
      st.payments.length > 0 ||
      st.missing_fields.length > 0 ||
      st.conflicts.length > 0
    );
  });

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h6">Your Financial Picture</Typography>
        <Typography variant="body2" color="text.secondary">
          Fills in as we talk through the next 30 days.
        </Typography>
      </Box>

      {!hasAnything && <EmptyState />}

      <ConflictsCard />
      <MissingInfoCard />
      <IncomeCard />
      <PaymentsCard />
      <ExpensesCard />
      <PlanCard />
    </Stack>
  );
}