import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 5 },   // 0 a 30s: Carga leve -> 4K
    { duration: '30s', target: 30 },  // 30 a 60s: Carga média -> 1080p
    { duration: '30s', target: 60 },  // 60 a 90s: Carga alta (Rush) -> 720p
    { duration: '10s', target: 0 },   // Resfriamento final
  ],
};

export default function () {
  http.get('http://api:8080/stream/authorize?user_id=usr_99823&movie_id=mov_escape_earth');
  sleep(0.1);
}