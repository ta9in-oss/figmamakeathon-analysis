import { useEffect, useRef } from 'react';
import { Chart, ScatterController, LinearScale, PointElement, Tooltip, Legend } from 'chart.js';
import { loadCSV, winnerColor, nonWinnerColor, gridColor, type Entry } from './loadData';

Chart.register(ScatterController, LinearScale, PointElement, Tooltip, Legend);

export default function EngagementScatter() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    loadCSV().then((data: Entry[]) => {
      const winners = data.filter(d => d.winner === 'True').map(d => ({ x: d.day_relative_to_open, y: d.engagement_score }));
      const nonWinners = data.filter(d => d.winner === 'False').map(d => ({ x: d.day_relative_to_open, y: d.engagement_score }));

      if (chartRef.current) chartRef.current.destroy();
      
      const ctx = canvasRef.current!;
      chartRef.current = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [
            { label: 'Winners', data: winners, backgroundColor: winnerColor(), pointRadius: 6, pointHoverRadius: 8 },
            { label: 'Non-Winners', data: nonWinners, backgroundColor: nonWinnerColor(), pointRadius: 5, pointHoverRadius: 7 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' }, tooltip: { callbacks: { label: (ctx: any) => `Day ${ctx.raw.x}, Score: ${ctx.raw.y}` } } },
          scales: {
            x: { title: { display: true, text: 'Day of Submission Window' }, grid: { color: gridColor() } },
            y: { title: { display: true, text: 'Engagement Score' }, grid: { color: gridColor() } },
          },
        },
      });
    });
  }, []);

  return <div style={{ height: '400px' }}><canvas ref={canvasRef}></canvas></div>;
}
