import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const formatMoney = (value: number | string) =>
  `R$ ${Number(value || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export interface ProjectionChartPoint {
  month: string;
  salário: number;
  gastos: number;
  intenções: number;
  sobra: number;
}

export const ProjectionChart: React.FC<{
  data: ProjectionChartPoint[];
  spendingGoal?: number | null;
}> = ({ data, spendingGoal }) => {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="month" fontSize={11} />
        <YAxis fontSize={11} width={45} />
        <Tooltip formatter={(value: number) => formatMoney(value)} />
        <Legend />
        <Line type="monotone" dataKey="salário" stroke="#3b82f6" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="gastos" stroke="#ef4444" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="intenções" stroke="#f59e0b" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="sobra" stroke="#10b981" strokeWidth={2} dot={false} />
        {spendingGoal != null && spendingGoal > 0 && (
          <ReferenceLine
            y={spendingGoal}
            stroke="#9ca3af"
            strokeDasharray="5 5"
            label={{ value: `Meta ${formatMoney(spendingGoal)}`, position: 'insideTopRight', fontSize: 11 }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
};
