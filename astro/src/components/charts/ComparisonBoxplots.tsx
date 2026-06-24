import { useEffect, useRef } from 'react';
import { Chart, BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { loadCSV, winnerColor, nonWinnerColor, gridColor, type Entry } from './loadData';

Chart.register(BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function quartiles(arr: number[]) {
  const sorted = [...arr].sort((a, b) => a - b);
  const q1 = sorted[Math.floor(sorted.length * 0.25)];
  const median = sorted[Math.floor(sorted.length * 0.5)];
  const q3 = sorted[Math.floor(sorted.length * 0.75)];
  const iqr = q3 - q1;
  const lower = Math.max(sorted[0], q1 - 1.5 * iqr);
  const upper = Math.min(sorted[sorted.length - 1], q3 + 1.5 * iqr);
  return { q1, median, q3, lower, upper };
}

export default function ComparisonBoxplots() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    loadCSV().then((data: Entry[]) => {
      const winners = data.filter(d => d.winner === 'True');
      const nonWinners = data.filter(d => d.winner === 'False');

      const metrics = [
        { key: 'day_relative_to_open' as keyof Entry, label: 'Posting Day' },
        { key: 'engagement_score' as keyof Entry, label: 'Engagement' },
        { key: 'creator_followers' as keyof Entry, label: 'Followers' },
        { key: 'social_platforms_count' as keyof Entry, label: 'Platforms' },
      ];

      const wQuartiles = metrics.map(m => quartiles(winners.map(w => w[m.key] as number)));
      const nwQuartiles = metrics.map(m => quartiles(nonWinners.map(w => w[m.key] as number)));

      // Render as grouped bar with error bars for IQR
      if (chartRef.current) chartRef.current.destroy();
      
      const ctx = canvasRef.current!;
      chartRef.current = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: metrics.map(m => m.label),
          datasets: [
            { label: 'Winners (median)', data: wQuartiles.map(q => q.median), backgroundColor: winnerColor(), borderRadius: 4 },
            { label: 'Non-Winners (median)', data: nwQuartiles.map(q => q.median), backgroundColor: nonWinnerColor(), borderRadius: 4 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } },
          scales: {
            y: { title: { display: true, text: 'Median Value' }, grid: { color: gridColor() }, beginAtZero: true },
            x: { grid: { color: gridColor() } },
          },
        },
      });
    });
  }, []);

  return <div style={{ height: '400px' }}><canvas ref={canvasRef}></canvas></div>;
}
