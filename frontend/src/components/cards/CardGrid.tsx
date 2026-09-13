import { Grid } from "@mui/material";
import { IncomeCard } from "./IncomeCard";
import { ExpensesCard } from "./ExpensesCard";
import { PaymentsCard } from "./PaymentsCard";
import { MissingInfoCard } from "./MissingInfoCard";
import { ConflictsCard } from "./ConflictsCard";
import { PlanCard } from "./PlanCard";

// Order matters: things needing attention (conflicts, missing info)
// surface above informational cards, and the plan — the end goal —
// sits at the bottom since it only appears once computed.
export function CardGrid() {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12}><ConflictsCard /></Grid>
      <Grid item xs={12}><MissingInfoCard /></Grid>
      <Grid item xs={12} md={6}><IncomeCard /></Grid>
      <Grid item xs={12} md={6}><PaymentsCard /></Grid>
      <Grid item xs={12}><ExpensesCard /></Grid>
      <Grid item xs={12}><PlanCard /></Grid>
    </Grid>
  );
}