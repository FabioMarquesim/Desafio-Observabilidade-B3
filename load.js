import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 5 },   // 0 a 30s: Carga leve
    { duration: '30s', target: 30 },  // 30 a 60s: Carga média
    { duration: '60s', target: 60 },  // 60 a 90s: Carga alta (Rush)
    { duration: '10s', target: 0 },   // Resfriamento final
  ],
};

// Executado antes do teste começar: ativa o modo correto na API com base na env var
export function setup() {
  const errorMode = __ENV.ERROR_MODE === 'true';
  const endpoint = errorMode 
    ? 'http://api:8080/rush/error-start' 
    : 'http://api:8080/rush/start';
  
  const res = http.post(endpoint);
  console.log(`[SETUP K6] Modo Chaos/Erros ativado: ${errorMode} (Status: ${res.status})`);
}

// Executado durante o teste de carga
export default function () {
  http.get('http://api:8080/stream/authorize?user_id=usr_99823&movie_id=mov_escape_earth');
  sleep(0.1);
}

// Executado após o término do teste: limpa o estado da API
export function teardown() {
  http.post('http://api:8080/rush/stop');
  console.log('[TEARDOWN K6] Rush finalizado e estado resetado na API.');
}