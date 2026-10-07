import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 50, // 50 usuarios virtuais simultaneos simulados
  duration: '5m', // Duracao total do teste
};

const tracks = [
  { artist: 'Foo Fighters', title: 'Everlong' },
  { artist: 'Daft Punk', title: 'One More Time' },
  { artist: 'Queen', title: 'Bohemian Rhapsody' },
  { artist: 'The Prodigy', title: 'Breathe' },
  { artist: 'Fred again..', title: 'Delilah' },
];

export default function () {
  const track = tracks[Math.floor(Math.random() * tracks.length)];
  const url = `http://api:8080/live-sync/track?artist=${encodeURIComponent(track.artist)}&title=${encodeURIComponent(track.title)}`;
  http.get(url);
  sleep(0.1); // Pausa de 100ms entre as requisicoes de cada usuario
}
