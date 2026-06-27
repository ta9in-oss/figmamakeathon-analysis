import { useEffect, useRef, useState } from 'react';
import { Chart, ScatterController, LinearScale, PointElement, Tooltip, Legend } from 'chart.js';
import { loadCSV, winnerColor, nonWinnerColor, gridColor, type Entry } from './loadData';

Chart.register(ScatterController, LinearScale, PointElement, Tooltip, Legend);

const EDITIONS = ['Figma Make-a-thon (Sep 2025)', 'Figma Makeathon March 2026', 'Config Makeathon 2026'];
const ED_LABELS = ['Sep 2025', 'Mar 2026', 'Config 2026'];

export default function WinnerTimeline() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef  = useRef<Chart | null>(null);
  const dataRef   = useRef<Entry[]>([]);
  const [edIdx, setEdIdx] = useState(0);

  function renderChart(data: Entry[], idx: number) {
    const ed = EDITIONS[idx];
    const subset = data.filter(d => d.edition === ed);
    const winners = subset.filter(d => d.winner === 'true').map(d => ({ x: d.day_relative_to_open, y: d.likes, label: d.creator_name }));
    const nonWins = subset.filter(d => d.winner === 'false').map(d => ({ x: d.day_relative_to_open, y: d.likes }));

    if (chartRef.current) chartRef.current.destroy();
    chartRef.current = new Chart(canvasRef.current!, {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: 'Non-Winners',
            data: nonWins,
            backgroundColor: nonWinnerColor() + '55',
            pointRadius: 3,
            pointHoverRadius: 5,
          },
          {
            label: 'Winners',
            data: winners,
            backgroundColor: winnerColor(),
            borderColor: winnerColor(),
            borderWidth: 1,
            pointRadius: 14,
            pointHoverRadius: 16,
            pointStyle: 'star',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: {
              label: (ctx: any) => {
                const pt = ctx.raw as any;
                const name = pt.label ? ` (${pt.label})` : '';
                return `Day ${pt.x}, ${pt.y} likes${name}`;
              }
            }
          }
        },
        scales: {
          x: { title: { display: true, text: 'Day into Contest Window' }, grid: { color: gridColor() }, beginAtZero: true },
          y: { title: { display: true, text: 'Likes' }, grid: { color: gridColor() }, beginAtZero: true },
        },
      },
    });
  }

  useEffect(() => {
    loadCSV().then((data: Entry[]) => {
      dataRef.current = data;
      renderChart(data, 0);
    });
  }, []);

  function switchEdition(idx: number) {
    setEdIdx(idx);
    if (dataRef.current.length) renderChart(dataRef.current, idx);
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
        {ED_LABELS.map((label, i) => (
          <button
            key={i}
            onClick={() => switchEdition(i)}
            style={{
              padding: '4px 12px',
              borderRadius: '6px',
              border: '1px solid var(--color-border)',
              background: edIdx === i ? '#1D9E75' : 'transparent',
              color: edIdx === i ? '#fff' : 'inherit',
              cursor: 'pointer',
              fontSize: '13px',
            }}
          >
            {label}
          </button>
        ))}
      </div>
      <div style={{ height: '400px' }}><canvas ref={canvasRef} /></div>
    </div>
  );
}
