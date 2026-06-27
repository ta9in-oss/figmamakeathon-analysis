import { useEffect, useRef } from 'react';
import { Chart, BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { loadCSV, winnerColor, nonWinnerColor, gridColor, type Entry } from './loadData';

Chart.register(BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const EDITIONS = ['Figma Make-a-thon (Sep 2025)', 'Figma Makeathon March 2026', 'Config Makeathon 2026'];
const ED_LABELS = ['Sep 2025', 'Mar 2026', 'Config 2026'];

function pct(arr: boolean[]) {
  return arr.length ? Math.round((arr.filter(Boolean).length / arr.length) * 100) : 0;
}

export default function VideoVsSocialChart() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef  = useRef<Chart | null>(null);

  useEffect(() => {
    loadCSV().then((data: Entry[]) => {
      // Labels: [Sep W, Sep NW, Mar W, Mar NW, Cfg W, Cfg NW] for video
      // Two metric groups: video% and avg social platforms
      const labels: string[] = [];
      const videoW: number[] = [];
      const videoNW: number[] = [];
      const socialW: number[] = [];
      const socialNW: number[] = [];

      EDITIONS.forEach((ed, i) => {
        const winners = data.filter(d => d.edition === ed && d.winner === 'true');
        const nw      = data.filter(d => d.edition === ed && d.winner === 'false');
        labels.push(ED_LABELS[i]);
        videoW.push(pct(winners.map(d => d.has_video === 'true')));
        videoNW.push(pct(nw.map(d => d.has_video === 'true')));
        const avgSocW  = winners.length ? winners.reduce((s, d) => s + d.social_platforms_count, 0) / winners.length : 0;
        const avgSocNW = nw.length ? nw.reduce((s, d) => s + d.social_platforms_count, 0) / nw.length : 0;
        socialW.push(Math.round(avgSocW * 100) / 100);
        socialNW.push(Math.round(avgSocNW * 100) / 100);
      });

      if (chartRef.current) chartRef.current.destroy();
      chartRef.current = new Chart(canvasRef.current!, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            { label: 'Winners with Video', data: videoW, backgroundColor: winnerColor(), borderRadius: 4, yAxisID: 'y' },
            { label: 'Non-Winners with Video', data: videoNW, backgroundColor: nonWinnerColor(), borderRadius: 4, yAxisID: 'y' },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.raw}%` } },
          },
          scales: {
            y: { grid: { color: gridColor() }, beginAtZero: true, max: 100, ticks: { callback: v => v + '%' }, title: { display: true, text: '% Posts with Video' } },
            x: { grid: { color: gridColor() } },
          },
        },
      });
    });
  }, []);

  return <div style={{ height: '360px' }}><canvas ref={canvasRef} /></div>;
}
