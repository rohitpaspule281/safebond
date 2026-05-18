"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

type EmotionDistributionChartProps = {
  data: {
    emotion: string;
    share: number;
    avg_intensity: number;
    color: string;
  }[];
};

export function EmotionDistributionChart({ data }: EmotionDistributionChartProps) {
  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, left: 12, bottom: 4 }}>
          <CartesianGrid stroke="rgba(87,121,109,0.1)" horizontal={false} />
          <XAxis
            type="number"
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#57796D", fontSize: 12 }}
          />
          <YAxis
            type="category"
            dataKey="emotion"
            tickLine={false}
            axisLine={false}
            width={90}
            tick={{ fill: "#2F3E3A", fontSize: 12 }}
          />
          <Tooltip
            cursor={{ fill: "rgba(255,255,255,0.6)" }}
            contentStyle={{
              borderRadius: 20,
              border: "1px solid rgba(255,255,255,0.85)",
              backgroundColor: "rgba(255,255,255,0.96)",
              boxShadow: "0 18px 42px rgba(35,55,49,0.12)"
            }}
            formatter={(value: number, name: string) => [
              `${value}%`,
              name === "share" ? "Share" : "Avg intensity"
            ]}
          />
          <Bar dataKey="share" radius={[0, 18, 18, 0]}>
            {data.map((item) => (
              <Cell key={item.emotion} fill={item.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
