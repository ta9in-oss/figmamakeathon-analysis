import { useEffect, useRef } from 'react';
import { Chart, BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js';
import { gridColor } from './loadData';

Chart.register(BarController, CategoryScale, LinearScale, BarElement, Tooltip, Legend);

// Staff post counts come from enhanced_analysis.py Q5 data baked in here.
// Sep 2025: 8 staff posts | Mar 2026: 5 | Config 2026: 5
// Participant posts: Sep=1771, Mar=1495, Config=946
const DATA = [
  { label: 'Sep 2025',     staff: 8,  participants: 1771 },
  { label: 'Mar 2026',     staff: 5,  participants: 1495 },
  { label: 'Config 2026',  staff: 5,  participants: 946  },
];

export default function StaffPresenceChart() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef  = useRef<Chart | null>(null);

  useEffect(() => {
    if (chartRef.current) chartRef.current.destroy();
    chartRef.current = new Chart(canvasRef.current!, {
      type: 'bar',
      data: {
        labels: DATA.map(d => d.label),
        datasets: [
          {
            label: 'Participant Posts',
            data: DATA.map(d => d.participants),
            backgroundColor: '#888780',
            borderRadius: 4,
            stack: 'stack',
          },
          {
            label: 'Contra Staff Posts',
            data: DATA.map(d => d.staff),
            backgroundColor: '#BA7517',
            borderRadius: 4,
            stack: 'stack',
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
              label: ctx => `${ctx.dataset.label}: ${ctx.raw}`,
              footer: items => {
                const total = items.reduce((s, i) => s + (i.raw as number), 0);
                return `Total: ${total}`;
              }
            }
          },
        },
        scales: {
          x: { stacked: true, grid: { color: gridColor() } },
          y: { stacked: true, grid: { color: gridColor() }, beginAtZero: true, title: { display: true, text: 'Post Count' } },
        },
      },
    });
  }, []);

  return (
    <div>
      <div style={{ height: '320px' }}><canvas ref={canvasRef} /></div>
      <p style={{ fontSize: '12px', color: 'var(--color-muted-foreground)', marginTop: '8px' }}>
        Staff includes: Gui Seiz (Contra CEO), Jan Mráz, Galaxia Wu, Sabrina Polanco, Daniela Muntyan.
        Staff posts are announcements, winner reveals, and community updates — not submissions.
        Reply/comment interactions are not shown (require post-level API calls).
      </p>
    </div>
  );
}
