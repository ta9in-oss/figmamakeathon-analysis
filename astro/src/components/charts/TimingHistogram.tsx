import { useEffect, useRef } from 'react';
import { Chart, BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { loadCSV, winnerColor, nonWinnerColor, gridColor, type Entry } from './loadData';

Chart.register(BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function TimingHistogram() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    loadCSV().then((data: Entry[]) => {
      const winners = data.filter(d => d.winner === 'True');
      const nonWinners = data.filter(d => d.winner === 'False');
      
      const maxDay = Math.max(...data.map(d => d.day_relative_to_open));
      const bins = Array.from({ length: maxDay }, (_, i) => i + 1);
      
      const winnerCounts = bins.map(day => winners.filter(d => Math.floor(d.day_relative_to_open) === day).length);
      const nonWinnerCounts = bins.map(day => nonWinners.filter(d => Math.floor(d.day_relative_to_open) === day).length);

      if (chartRef.current) chartRef.current.destroy();
      
      const ctx = canvasRef.current!;
      chartRef.current = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: bins.map(String),
          datasets: [
            { label: 'Winners', data: winnerCounts, backgroundColor: winnerColor(), borderRadius: 4 },
            { label: 'Non-Winners', data: nonWinnerCounts, backgroundColor: nonWinnerColor(), borderRadius: 4 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } },
          scales: {
            x: { title: { display: true, text: 'Day of Submission Window' }, grid: { color: gridColor() } },
            y: { title: { display: true, text: 'Number of Entries' }, grid: { color: gridColor() }, beginAtZero: true },
          },
        },
      });
    });
  }, []);

  return <div style={{ height: '400px' }}><canvas ref={canvasRef}></canvas></div>;
}
