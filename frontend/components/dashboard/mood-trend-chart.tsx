"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { moodTrend } from "@/lib/mock-data";

type MoodTrendChartProps = {
  data?: { day: string; calm: number; stress: number; loneliness: number }[];
};

export function MoodTrendChart({ data = moodTrend }: MoodTrendChartProps) {
  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 12, right: 8, left: -18, bottom: 0 }}>
          <CartesianGrid stroke="rgba(87,121,109,0.12)" vertical={false} />
          <XAxis
            dataKey="day"
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#57796D", fontSize: 12 }}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#57796D", fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 20,
              border: "1px solid rgba(255,255,255,0.8)",
              backgroundColor: "rgba(255,255,255,0.94)",
              boxShadow: "0 20px 45px rgba(40,55,49,0.12)"
            }}
          />
          <Legend iconType="circle" />
          <Line
            type="monotone"
            dataKey="calm"
            stroke="#3C8D7D"
            strokeWidth={3}
            dot={{ r: 0 }}
            activeDot={{ r: 5, fill: "#3C8D7D" }}
          />
          <Line
            type="monotone"
            dataKey="stress"
            stroke="#E86C52"
            strokeWidth={2.5}
            dot={{ r: 0 }}
            activeDot={{ r: 5, fill: "#E86C52" }}
          />
          <Line
            type="monotone"
            dataKey="loneliness"
            stroke="#5A8FD8"
            strokeWidth={2.5}
            dot={{ r: 0 }}
            activeDot={{ r: 5, fill: "#5A8FD8" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
