export interface Entry {
  edition: string;
  entry_id: string;
  day_relative_to_open: number;
  days_before_deadline: number;
  project_title: string;
  creator_name: string;
  likes: number;
  comments: number;
  engagement_score: number;
  winner: string;
  winner_category: string;
  creator_followers: number;
  social_platforms_count: number;
  in_contra_recap: string;
  in_figma_blog: string;
  video_url: string;
  cross_posted_x: string;
  cross_posted_linkedin: string;
  cross_posted_instagram: string;
  cross_posted_threads: string;
  cross_posted_bluesky: string;
}

export async function loadCSV(): Promise<Entry[]> {
  const resp = await fetch('/data/all_entries.csv');
  const text = await resp.text();
  const lines = text.trim().split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const vals = line.split(',');
    const obj: any = {};
    headers.forEach((h, i) => {
      const v = vals[i];
      if (['day_relative_to_open', 'days_before_deadline', 'likes', 'comments',
           'engagement_score', 'creator_followers', 'social_platforms_count'].includes(h)) {
        obj[h] = parseFloat(v) || 0;
      } else {
        obj[h] = v;
      }
    });
    return obj as Entry;
  });
}

export function winnerColor() { return '#1D9E75'; }           /* Teal 400 */
export function nonWinnerColor() { return '#888780'; }        /* Gray 400 */
export function accentColor() { return '#BA7517'; }            /* Amber 400 */
export function highlightColor() { return '#BA7517'; }         /* Amber 400 */
export function gridColor() { return '#D3D1C7'; }             /* Border */
