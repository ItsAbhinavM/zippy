import { Card, CardContent, Typography, Stack, Chip, Divider, Box } from "@mui/material";
import { useFinancialStore } from "../../store/useFinancialStore";

const KIND_COLOR: Record<string, string> = {
  income: "success.main",
  essential_payment: "text.primary",
  debt_payment: "secondary.main",
  optional_expense: "text.secondary",
  optional_cut: "warning.main",
};

export function PlanCard() {
  const plan = useFinancialStore((s) => s.plan);
  if (!plan) return null;

  return (
    <Card sx={{ borderLeft: "4px solid", borderColor: plan.is_solvable ? "success.main" : "error.main" }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Your 30-Day Plan</Typography>
          <Chip label={plan.is_solvable ? "Manageable" : "Shortfall remains"} color={plan.is_solvable ? "success" : "error"} />
        </Stack>

        <Stack direction="row" spacing={3} mb={2} flexWrap="wrap">
          <Box>
            <Typography variant="caption" color="text.secondary">Monthly headroom</Typography>
            <Typography variant="h6">₹{plan.monthly_headroom.toLocaleString()}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Net position</Typography>
            <Typography variant="h6">₹{plan.net_position.toLocaleString()}</Typography>
          </Box>
        </Stack>

        <Divider sx={{ mb: 2 }} />

        <Typography variant="subtitle2" gutterBottom>What to do, in order</Typography>
        <Stack spacing={1.25}>
          {plan.action_plan.map((step) => (
            <Stack key={step.order} direction="row" spacing={1.5} alignItems="flex-start">
              <Box
                sx={{
                  minWidth: 24, height: 24, borderRadius: "50%",
                  bgcolor: "background.default", border: "1px solid", borderColor: "divider",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 12, fontWeight: 700, flexShrink: 0, mt: 0.25,
                }}
              >
                {step.order}
              </Box>
              <Box flex={1}>
                <Typography variant="body2" sx={{ color: KIND_COLOR[step.kind] }}>
                  {step.instruction}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(step.day).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                  {" · balance after: ₹"}{step.running_balance_after.toLocaleString()}
                </Typography>
              </Box>
            </Stack>
          ))}
        </Stack>

        {plan.assumptions.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
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