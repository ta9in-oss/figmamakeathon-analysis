import { useEffect, useRef } from 'react';
import { Chart, BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { loadCSV, winnerColor, nonWinnerColor, gridColor, type Entry } from './loadData';

Chart.register(BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function RecapChart() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    loadCSV().then((data: Entry[]) => {
      const winners = data.filter(d => d.winner === 'true');
      const nonWinners = data.filter(d => d.winner === 'false');

      const pct = (arr: Entry[], field: keyof Entry) => 
        (arr.filter(d => d[field] === 'True').length / arr.length) * 100;

      const wContra = pct(winners, 'in_contra_recap');
      const nwContra = pct(nonWinners, 'in_contra_recap');
      const wBlog = pct(winners, 'in_figma_blog');
      const nwBlog = pct(nonWinners, 'in_figma_blog');

      if (chartRef.current) chartRef.current.destroy();
      
      const ctx = canvasRef.current!;
      chartRef.current = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['In Contra Recap', 'In Figma Blog'],
          datasets: [
            { label: 'Winners', data: [wContra, wBlog], backgroundColor: winnerColor(), borderRadius: 4 },
            { label: 'Non-Winners', data: [nwContra, nwBlog], backgroundColor: nonWinnerColor(), borderRadius: 4 },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } },
          scales: {
            y: { title: { display: true, text: 'Percentage (%)' }, grid: { color: gridColor() }, beginAtZero: true, max: 100 },
            x: { grid: { color: gridColor() } },
          },
        },
      });
    });
  }, []);

  return <div style={{ height: '350px' }}><canvas ref={canvasRef}></canvas></div>;
}
