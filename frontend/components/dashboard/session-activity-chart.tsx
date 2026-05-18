"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

type SessionActivityChartProps = {
  data: {
    day: string;
    messages: number;
    avg_words: number;
    reflection_depth: number;
  }[];
};

export function SessionActivityChart({ data }: SessionActivityChartProps) {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 12, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="sessionMessages" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#5A8FD8" stopOpacity={0.55} />
              <stop offset="100%" stopColor="#5A8FD8" stopOpacity={0.06} />
            </linearGradient>
          </defs>
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
          <Area
            type="monotone"
            dataKey="messages"
            fill="url(#sessionMessages)"
            stroke="#5A8FD8"
            strokeWidth={2.5}
          />
          <Line
            type="monotone"
            dataKey="reflection_depth"
            stroke="#C15D84"
            strokeWidth={3}
            dot={{ r: 0 }}
            activeDot={{ r: 5, fill: "#C15D84" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
