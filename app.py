<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>外貨換算アプリ</title>
<style>
  /* 全体のレイアウト調整 */
  body { 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
    padding: 15px; 
    line-height: 1.6;
    background-color: #f8f9fa;
    color: #333;
    max-width: 500px; /* PCで見ても広がりすぎないように制限 */
    margin: 0 auto;
  }
  h2 { font-size: 1.4em; color: #000; border-left: 5px solid #007bff; padding-left: 10px; }
  h3 { font-size: 1.2em; margin-top: 20px; }

  /* 入力項目をスマホで押しやすくする */
  div { margin-bottom: 12px; }
  label { display: block; font-weight: bold; font-size: 0.9em; margin-bottom: 2px; }
  
  input, select { 
    width: 100%; /* 横幅いっぱいに広げる */
    box-sizing: border-box; 
    padding: 12px; /* タップしやすい高さ */
    font-size: 16px; /* iPhoneでズームされないための最小サイズ */
    border: 1px solid #ccc;
    border-radius: 6px;
    background: #fff;
  }

  /* ボタンのスタイル */
  button { 
    padding: 12px 15px; 
    font-size: 16px; 
    border-radius: 6px; 
    border: none; 
    background-color: #e0e0e0; 
    cursor: pointer;
    margin: 4px 2px;
    transition: background 0.2s;
  }
  /* メインの計算ボタンを目立たせる */
  button[onclick="calculate()"] {
    background-color: #007bff;
    color: white;
    width: 100%;
    font-weight: bold;
    margin-top: 10px;
  }
  button:active { opacity: 0.7; }

  /* 履歴エリア */
  .log-item { 
    background: white;
    border: 1px solid #eee;
    border-radius: 4px;
    margin-bottom: 5px;
    padding: 10px;
    font-size: 0.85em;
    word-break: break-all;
  }
  .error { color: #dc3545; font-size: 0.85em; margin-top: 4px; display: none; font-weight: bold; }
  
  hr { border: 0; border-top: 1px solid #ddd; margin: 20px 0; }

  /* 結果表示 */
  #result { color: #d63384; font-size: 1.5em; font-weight: bold; }

  /* 横並びボタン用 */
  .button-group { display: flex; flex-wrap: wrap; gap: 5px; }
  .button-group button { flex: 1; min-width: 100px; }
</style>
</head>
<body>

<h2>外貨 → 円 換算アプリ</h2>

<div>
  <label>日付:</label>
  <input type="date" id="date">
  <button type="button" style="width: auto; padding: 8px 15px;" onclick="openRate()">為替ページを開く</button>
</div>

<div>
  <label>通貨:</label>
  <select id="currency">
    <option value="USD">USD (ドル)</option>
    <option value="EUR">EUR (ユーロ)</option>
    <option value="GBP">GBP (ポンド)</option>
    <option value="AUD">AUD (豪ドル)</option>
  </select>
</div>

<hr>

<div>
  <label>レート:</label>
  <input type="number" id="rate" step="0.0001" placeholder="例: 150.25">
  <button type="button" style="width: auto; font-size: 12px; padding: 5px 10px;" onclick="clearRate()">レートクリア</button>
  <span class="error" id="rateError">正しいレートを入力してください</span>
</div>

<div>
  <label>外貨金額:</label>
  <input type="number" id="amount" step="0.01" placeholder="例: 100.00">
  <span class="error" id="amountError">正しい金額を入力してください</span>
</div>

<div>
  <label>端数処理:</label>
  <select id="rounding">
    <option value="round">四捨五入</option>
    <option value="ceil">切り上げ</option>
    <option value="floor">切り捨て</option>
  </select>
</div>

<button onclick="calculate()">計算する</button>

<div class="button-group" style="margin-top: 10px;">
  <button onclick="clearInput()">入力クリア</button>
  <button onclick="clearLog()">履歴クリア</button>
</div>

<h3>換算結果: <span id="result">-</span> 円</h3>

<div>
  <h3>履歴</h3>
  <div id="log"></div>
</div>

<script>
const logList = [];

// =========================
// 日本祝日判定（変更なし）
// =========================
function isBaseHoliday(date) {
  const y = date.getFullYear();
  const m = date.getMonth() + 1;
  const d = date.getDate();
  if (m === 1 && d === 1) return true;
  if (y >= 1967 && m === 2 && d === 11) return true;
  if (y >= 2020 && m === 2 && d === 23) return true;
  if (y >= 1989 && y <= 2018 && m === 12 && d === 23) return true;
  if (y >= 2007 && m === 4 && d === 29) return true;
  if (y >= 1989 && y <= 2006 && m === 4 && d === 29) return true;
  if (m === 5 && d === 3) return true;
  if (y >= 2007 && m === 5 && d === 4) return true;
  if (m === 5 && d === 5) return true;
  if (y >= 2016 && m === 8 && d === 11) return true;
  if (m === 11 && d === 3) return true;
  if (m === 11 && d === 23) return true;
  function getNthMonday(year, month, nth) {
    const first = new Date(year, month - 1, 1);
    const offset = (1 - first.getDay() + 7) % 7;
    return 1 + offset + (nth - 1) * 7;
  }
  if (y >= 2000 && m === 1 && d === getNthMonday(y, 1, 2)) return true;
  if (y >= 2003 && m === 7 && d === getNthMonday(y, 7, 3)) return true;
  if (y >= 2003 && m === 9 && d === getNthMonday(y, 9, 3)) return true;
  if (y >= 2022 && m === 10 && d === getNthMonday(y, 10, 2)) return true;
  if (y === 2020 && m === 7 && d === 24) return true;
  if (y === 2021 && m === 7 && d === 23) return true;
  if (y >= 1980 && y <= 2099) {
    const spring = Math.floor(20.8431 + 0.242194 * (y - 1980) - Math.floor((y - 1980) / 4));
    if (m === 3 && d === spring) return true;
    const autumn = Math.floor(23.2488 + 0.242194 * (y - 1980) - Math.floor((y - 1980) / 4));
    if (m === 9 && d === autumn) return true;
  }
  const prev = new Date(y, m - 1, d - 1);
  const next = new Date(y, m - 1, d + 1);
  if (isKokuminNoKyujitsu(date, prev, next)) return true;
  return false;
}

function isKokuminNoKyujitsu(date, prev, next) {
  const w = date.getDay();
  if (w === 0 || w === 6) return false;
  return isBaseHolidaySimple(prev) && isBaseHolidaySimple(next);
}

function isBaseHolidaySimple(date) {
  const y = date.getFullYear();
  const m = date.getMonth() + 1;
  const d = date.getDate();
  if (m === 1 && d === 1) return true;
  if (y >= 1967 && m === 2 && d === 11) return true;
  if (y >= 2020 && m === 2 && d === 23) return true;
  if (m === 4 && d === 29) return true;
  if (m === 5 && d === 3) return true;
  if (y >= 2007 && m === 5 && d === 4) return true;
  if (m === 5 && d === 5) return true;
  if (y >= 2016 && m === 8 && d === 11) return true;
  if (m === 11 && d === 3) return true;
  if (m === 11 && d === 23) return true;
  function getNthMonday(year, month, nth) {
    const first = new Date(year, month - 1, 1);
    const offset = (1 - first.getDay() + 7) % 7;
    return 1 + offset + (nth - 1) * 7;
  }
  if (y >= 2000 && m === 1 && d === getNthMonday(y, 1, 2)) return true;
  if (y >= 2003 && m === 7 && d === getNthMonday(y, 7, 3)) return true;
  if (y >= 2003 && m === 9 && d === getNthMonday(y, 9, 3)) return true;
  if (y >= 2022 && m === 10 && d === getNthMonday(y, 10, 2)) return true;
  if (y >= 1980 && y <= 2099) {
    const spring = Math.floor(20.8431 + 0.242194 * (y - 1980) - Math.floor((y - 1980) / 4));
    if (m === 3 && d === spring) return true;
    const autumn = Math.floor(23.2488 + 0.242194 * (y - 1980) - Math.floor((y - 1980) / 4));
    if (m === 9 && d === autumn) return true;
  }
  return false;
}

// =========================
// 振替休日判定（修正版のまま維持）
// =========================
function isJapaneseHoliday(date) {
  if (isBaseHoliday(date)) return true;
  let checkDate = new Date(date);
  while (true) {
    checkDate.setDate(checkDate.getDate() - 1);
    if (isBaseHoliday(checkDate)) {
      if (checkDate.getDay() === 0) return true;
    } else {
      break;
    }
  }
  return false;
}

// =========================
// 為替ページ
// =========================
function openRate() {
  const input = document.getElementById("date").value;
  if (!input) {
    alert("日付を入力してください");
    return;
  }
  const [iy, im, id] = input.split("-").map(Number);
  let date = new Date(iy, im - 1, id);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (date > today) {
    alert("未来の日付は指定できません");
    return;
  }
  let count = 0;
  const MAX_RETRY = 30;
  while (count < MAX_RETRY) {
    const w = date.getDay();
    if (w === 0 || w === 6 || isJapaneseHoliday(date)) {
      date.setDate(date.getDate() - 1);
      count++;
    } else
