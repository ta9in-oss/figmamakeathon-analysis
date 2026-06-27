import { useEffect, useRef } from 'react';
import { Chart, BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { loadCSV, gridColor, type Entry } from './loadData';

Chart.register(BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

// Distinct from winner/non-winner teal and gray so edition bars don't imply "winner"
const EDITION_COLORS = ['#3B82F6', '#BA7517', '#8B5CF6'];
const TIERS = ['0 likes', '1–5', '6–20', '21–50', '50+'];
const EDITION_LABELS = ['Sep 2025', 'Mar 2026', 'Config 2026'];
const EDITION_KEYS = ['Figma Make-a-thon (Sep 2025)', 'Figma Makeathon March 2026', 'Config Makeathon 2026'];

function tierOf(likes: number): number {
  if (likes === 0) return 0;
  if (likes <= 5) return 1;
  if (likes <= 20) return 2;
  if (likes <= 50) return 3;
  return 4;
}

export default function EngagementDistribution() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef  = useRef<Chart | null>(null);

  useEffect(() => {
    loadCSV().then((data: Entry[]) => {
      const datasets = EDITION_KEYS.map((ed, idx) => {
        const subset = data.filter(d => d.edition === ed);
        const counts = Array(5).fill(0);
        subset.forEach(d => counts[tierOf(d.likes)]++);
        const total = subset.length || 1;
        return {
          label: EDITION_LABELS[idx],
          data: counts.map(c => Math.round((c / total) * 100)),
          backgroundColor: EDITION_COLORS[idx],
          borderRadius: 4,
        };
      });

      if (chartRef.current) chartRef.current.destroy();
      chartRef.current = new Chart(canvasRef.current!, {
        type: 'bar',
        data: { labels: TIERS, datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' }, tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.raw}%` } } },
          scales: {
            x: { grid: { color: gridColor() }, title: { display: true, text: 'Likes Received' } },
            y: { grid: { color: gridColor() }, beginAtZero: true, title: { display: true, text: '% of Posts' }, ticks: { callback: v => v + '%' } },
          },
        },
      });
    });
  }, []);

  return <div style={{ height: '380px' }}><canvas ref={canvasRef} /></div>;
}
