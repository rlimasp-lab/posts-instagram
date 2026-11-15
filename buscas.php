<?php
// Registro anonimo das buscas do Placar do Desconto (sem IP, sem cookies).
// POST t=<termo>&r=<0|1>  -> registra (r=1 se o site encontrou produtos)
// GET ?top                -> termos sem resultado mais buscados nos ultimos 14 dias (2 ou mais buscas)
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
$dir = dirname(__DIR__) . '/placar_dados';
if (!is_dir($dir)) { @mkdir($dir, 0750, true); }
$log = $dir . '/buscas.log';

function limpa($s) {
  $s = mb_strtolower(trim((string)$s), 'UTF-8');
  $s = preg_replace('/[^\p{L}\p{N} ".,\/-]+/u', ' ', $s);
  $s = preg_replace('/\s+/u', ' ', $s);
  return mb_substr(trim($s), 0, 60, 'UTF-8');
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  $t = limpa($_POST['t'] ?? '');
  if (mb_strlen($t, 'UTF-8') < 2) { http_response_code(204); exit; }
  if (file_exists($log) && filesize($log) > 2000000) { @rename($log, $log . '.1'); }
  $r = (($_POST['r'] ?? '0') === '1') ? '1' : '0';
  @file_put_contents($log, gmdate('Y-m-d') . "\t" . $r . "\t" . $t . "\n", FILE_APPEND | LOCK_EX);
  http_response_code(204);
  exit;
}

if (isset($_GET['top'])) {
  $lim = gmdate('Y-m-d', time() - 14 * 86400);
  $cont = [];
  if (file_exists($log)) {
    foreach (file($log, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $l) {
      $p = explode("\t", $l, 3);
      if (count($p) < 3 || $p[0] < $lim || $p[1] !== '0') continue;
      $cont[$p[2]] = ($cont[$p[2]] ?? 0) + 1;
    }
  }
  $cont = array_filter($cont, function ($n) { return $n >= 2; });
  arsort($cont);
  $out = [];
  foreach (array_slice($cont, 0, 20, true) as $t => $n) { $out[] = ['termo' => $t, 'buscas' => $n]; }
  echo json_encode(['desde' => $lim, 'sem_resultado' => $out], JSON_UNESCAPED_UNICODE);
  exit;
}
http_response_code(400);
echo '{}';
