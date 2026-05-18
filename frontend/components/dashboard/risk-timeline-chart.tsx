"use client";

import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

type RiskTimelineChartProps = {
  data: {
    day: string;
    avg_risk: number;
    elevated: number;
    high_alerts: number;
  }[];
};

export function RiskTimelineChart({ data }: RiskTimelineChartProps) {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 10, right: 12, left: -16, bottom: 0 }}>
          <CartesianGrid stroke="rgba(87,121,109,0.1)" vertical={false} />
          <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fill: "#57796D", fontSize: 12 }} />
          <YAxis tickLine={false} axisLine={false} tick={{ fill: "#57796D", fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              borderRadius: 20,
              border: "1px solid rgba(255,255,255,0.85)",
              backgroundColor: "rgba(255,255,255,0.96)",
              boxShadow: "0 18px 42px rgba(35,55,49,0.12)"
            }}
          />
          <Legend iconType="circle" />
          <Bar dataKey="elevated" fill="#F2B166" radius={[10, 10, 0, 0]} />
          <Bar dataKey="high_alerts" fill="#E86C52" radius={[10, 10, 0, 0]} />
          <Line
            type="monotone"
            dataKey="avg_risk"
            stroke="#6E56CF"
            strokeWidth={3}
            dot={{ r: 0 }}
            activeDot={{ r: 5, fill: "#6E56CF" }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
