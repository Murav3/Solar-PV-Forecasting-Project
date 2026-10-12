const http = require('http');
const fs = require('fs');
const WebSocket = require('ws');

function getWebSocketUrl() {
  return new Promise((resolve, reject) => {
    http.get('http://127.0.0.1:9333/json', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const targets = JSON.parse(data);
          const page = targets.find(t => t.type === 'page' && t.url.includes('localhost:8000'));
          if (page && page.webSocketDebuggerUrl) resolve(page.webSocketDebuggerUrl);
          else reject(new Error('No matching page target found'));
        } catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function sendCommand(ws, method, params = {}) {
  return new Promise((resolve) => {
    const id = Math.floor(Math.random() * 1000000);
    const handler = (data) => {
      const msg = JSON.parse(data.toString());
      if (msg.id === id) {
        ws.off('message', handler);
        resolve(msg.result);
      }
    };
    ws.on('message', handler);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function run() {
  const wsUrl = await getWebSocketUrl();
  const ws = new WebSocket(wsUrl);
  await new Promise(r => ws.on('open', r));

  // 1. Switch to Fast Storm
  console.log('Testing Fast Storm scenario...');
  await sendCommand(ws, 'Runtime.evaluate', {
    expression: `
      setCloudScenario('fast');
      radarSimProgress = 45;
      onRadarScrubber(45);
    `
  });
  await new Promise(r => setTimeout(r, 600));

  const fastShot = await sendCommand(ws, 'Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('scratch/scenario_fast_verified.png', Buffer.from(fastShot.data, 'base64'));
  console.log('Saved scratch/scenario_fast_verified.png');

  // 2. Switch to Slow Heavy Fog
  console.log('Testing Slow Heavy Fog scenario...');
  await sendCommand(ws, 'Runtime.evaluate', {
    expression: `
      setCloudScenario('slow');
      radarSimProgress = 45;
      onRadarScrubber(45);
    `
  });
  await new Promise(r => setTimeout(r, 600));

  const slowShot = await sendCommand(ws, 'Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('scratch/scenario_slow_verified.png', Buffer.from(slowShot.data, 'base64'));
  console.log('Saved scratch/scenario_slow_verified.png');

  // 3. Reset back to moderate (normal)
  await sendCommand(ws, 'Runtime.evaluate', {
    expression: `
      setCloudScenario('moderate');
      radarSimProgress = 0;
      onRadarScrubber(0);
    `
  });

  ws.close();
}

run().catch(console.error);
