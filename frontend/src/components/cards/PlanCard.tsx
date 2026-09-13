import { Card, CardContent, Typography, Stack, Chip, Divider, List, ListItem, ListItemText } from "@mui/material";
import { useFinancialStore } from "../../store/useFinancialStore";

export function PlanCard() {
  const plan = useFinancialStore((s) => s.plan);
  if (!plan) return null;

  return (
    <Card sx={{ borderLeft: "4px solid", borderColor: plan.is_solvable ? "success.main" : "error.main" }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="h6">30-Day Plan</Typography>
          <Chip
            label={plan.is_solvable ? "Manageable" : "Shortfall remains"}
            color={plan.is_solvable ? "success" : "error"}
          />
        </Stack>

        <Stack spacing={0.5} mb={2}>
          <Typography variant="body2">Total income: ₹{plan.total_income.toLocaleString()}</Typography>
          <Typography variant="body2">Essential + debt payments: ₹{plan.total_essential.toLocaleString()}</Typography>
          <Typography variant="body2">Optional spending: ₹{plan.total_optional.toLocaleString()}</Typography>
          <Typography variant="body2" fontWeight={600}>
            Net position: ₹{plan.net_position.toLocaleString()}
          </Typography>
        </Stack>

        {plan.shortfall_days.length > 0 && (
          <Typography variant="body2" color="error.main" mb={2}>
            Shortfall on {plan.shortfall_days.length} day(s) during the month.
          </Typography>
        )}

        {plan.suggested_cuts.length > 0 && (
          <>
            <Divider sx={{ mb: 1 }} />
            <Typography variant="subtitle2" gutterBottom>Suggested cuts to stay afloat</Typography>
            <List dense disablePadding>
              {plan.suggested_cuts.map((c) => (
                <ListItem key={c.expense_id} disableGutters>
                  <ListItemText
                    primary={`${c.label}: cut ₹${c.cut_amount.toLocaleString()} of ₹${c.original_amount.toLocaleString()}`}
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}

        {plan.assumptions.length > 0 && (
          <>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle2" gutterBottom>Assumptions made</Typography>
            <Stack spacing={0.5}>
              {plan.assumptions.map((a, i) => (
                <Typography key={i} variant="caption" color="text.secondary">• {a.description}</Typography>
              ))}
            </Stack>
          </>
        )}
      </CardContent>
    </Card>
  );
}