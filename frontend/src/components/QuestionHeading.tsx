import { Typography, Box } from "@mui/material";
import { useFinancialStore } from "../store/useFinancialStore";

export function QuestionHeading() {
  const question = useFinancialStore((s) => s.currentQuestion);
  if (!question) return null;

  return (
    <Box sx={{ mb: 1 }}>
      <Typography
        variant="h4"
        sx={{ fontWeight: 800, color: "text.primary", lineHeight: 1.15 }}
      >
        {question}
      </Typography>
    </Box>
  );
}