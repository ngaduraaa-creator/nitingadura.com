#!/usr/bin/env node
// Pings IndexNow (Bing/Yandex) and Google Search Console to re-crawl
// Usage: node scripts/indexnow-ping.js

const https = require('https');
const fs = require('fs');
const path = require('path');

const KEY = fs.readFileSync(path.join(__dirname, '..', 'indexnow.key'), 'utf8').trim();
const HOST = 'nitingadura.com';

// Read sitemap and extract all URLs
const sitemap = fs.readFileSync(path.join(__dirname, '..', 'sitemap.xml'), 'utf8');
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]);

console.log(`Found ${urls.length} URLs to ping`);

// IndexNow API
function pingIndexNow(urlList) {
  const body = JSON.stringify({
    host: HOST,
    key: KEY,
    keyLocation: `https://${HOST}/${KEY}.txt`,
    urlList
  });

  const options = {
    hostname: 'api.indexnow.org',
    path: '/indexnow',
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
  };

  return new Promise((res, rej) => {
    const req = https.request(options, r => {
      let d = '';
      r.on('data', c => d += c);
      r.on('end', () => { console.log(`IndexNow: ${r.statusCode} — ${d.substring(0,100)}`); res(); });
    });
    req.on('error', rej);
    req.write(body);
    req.end();
  });
}

// Send in batches of 100
(async () => {
  for (let i = 0; i < urls.length; i += 100) {
    const batch = urls.slice(i, i + 100);
    console.log(`Pinging batch ${Math.floor(i/100)+1}: ${batch.length} URLs`);
    await pingIndexNow(batch);
    await new Promise(r => setTimeout(r, 1000));
  }
  console.log('Done');
})();
