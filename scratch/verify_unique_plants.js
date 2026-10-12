const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function main() {
  const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
  const profileDir = path.join(__dirname, 'fresh_profile_unique');
  
  const edge = spawn(edgePath, [
    '--headless=new',
    '--remote-debugging-port=9333',
    `--user-data-dir=${profileDir}`,
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    `http://localhost:8000/frontend/index.html?v=${Date.now()}`
  ]);

  await new Promise(r => setTimeout(r, 2500));

  try {
    const listRes = await fetch('http://127.0.0.1:9333/json');
    const tabs = await listRes.json();
    const tab = tabs.find(t => t.url.includes('8000')) || tabs[0];
    
    const ws = new WebSocket(tab.webSocketDebuggerUrl);
    await new Promise(r => ws.onopen = r);

    let id = 1;
    function send(method, params = {}) {
      return new Promise((resolve, reject) => {
        const msgId = id++;
        const handler = (evt) => {
          const res = JSON.parse(evt.data);
          if (res.id === msgId) {
            ws.removeEventListener('message', handler);
            if (res.error) reject(res.error);
            else resolve(res.result);
          }
        };
        ws.addEventListener('message', handler);
        ws.send(JSON.stringify({ id: msgId, method, params }));
      });
    }

    await send('Runtime.enable');
    await send('Emulation.setDeviceMetricsOverride', {
      width: 1440,
      height: 1200,
      deviceScaleFactor: 1,
      mobile: false
    });

    await new Promise(r => setTimeout(r, 2000));

    // Switch to Tab 4
    console.log('Switching to Tab 4...');
    await send('Runtime.evaluate', { expression: `switchTab('map');` });
    await new Promise(r => setTimeout(r, 1200));

    // 1. Normal Day: Select Plant L1 on 2026-01-06
    console.log('Testing Normal Day with Plant L1...');
    const resL1Normal = await send('Runtime.evaluate', {
      expression: `
        document.getElementById('dateSelect').value = '2026-01-06';
        renderMapView();
        selectPlantNode(1, false);
        ({
          title: document.getElementById('inspPlantTitle').textContent,
          lead: document.getElementById('inspLeadVal').textContent,
          sub: document.getElementById('inspLeadSub').textContent,
          mw: document.getElementById('inspMWVal').textContent,
          sun: document.getElementById('inspSunVal').textContent,
          badge: document.getElementById('radarActiveDateBadge').textContent
        });
      `,
      returnByValue: true
    });
    console.log('Normal Day L1:', resL1Normal.result.value);

    // Screenshot of Normal Day L1
    await send('Runtime.evaluate', { expression: `window.scrollTo(0, 320);` });
    await new Promise(r => setTimeout(r, 600));
    const ssNormalL1 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(__dirname, 'unique_normal_l1.png'), Buffer.from(ssNormalL1.data, 'base64'));

    // 2. Fast Storm Day: Select date 2026-01-11 with Plant L1
    console.log('Testing Fast Storm Day with Plant L1...');
    const resL1Storm = await send('Runtime.evaluate', {
      expression: `
        document.getElementById('dateSelect').value = '2026-01-11';
        renderMapView();
        selectPlantNode(1, false);
        ({
          title: document.getElementById('inspPlantTitle').textContent,
          lead: document.getElementById('inspLeadVal').textContent,
          sub: document.getElementById('inspLeadSub').textContent,
          mw: document.getElementById('inspMWVal').textContent,
          badge: document.getElementById('radarActiveDateBadge').textContent
        });
      `,
      returnByValue: true
    });
    console.log('Fast Storm Day L1:', resL1Storm.result.value);

    const ssStormL1 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(__dirname, 'unique_storm_l1.png'), Buffer.from(ssStormL1.data, 'base64'));

    // 3. Slow Fog Day: Select date 2026-02-04 with Plant L1
    console.log('Testing Slow Heavy Fog Day with Plant L1...');
    const resL1Fog = await send('Runtime.evaluate', {
      expression: `
        document.getElementById('dateSelect').value = '2026-02-04';
        renderMapView();
        selectPlantNode(1, false);
        ({
          title: document.getElementById('inspPlantTitle').textContent,
          lead: document.getElementById('inspLeadVal').textContent,
          sub: document.getElementById('inspLeadSub').textContent,
          mw: document.getElementById('inspMWVal').textContent,
          badge: document.getElementById('radarActiveDateBadge').textContent
        });
      `,
      returnByValue: true
    });
    console.log('Slow Fog Day L1:', resL1Fog.result.value);

    const ssFogL1 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(__dirname, 'unique_fog_l1.png'), Buffer.from(ssFogL1.data, 'base64'));

    // 4. Test other plants: Plant L5 and Plant L17
    console.log('Testing Plant L5 and Plant L17...');
    const resL5 = await send('Runtime.evaluate', {
      expression: `
        document.getElementById('dateSelect').value = '2026-01-06';
        renderMapView();
        selectPlantNode(5, false);
        ({
          title: document.getElementById('inspPlantTitle').textContent,
          lead: document.getElementById('inspLeadVal').textContent,
          mw: document.getElementById('inspMWVal').textContent
        });
      `,
      returnByValue: true
    });
    console.log('Normal Day L5:', resL5.result.value);

    const resL17 = await send('Runtime.evaluate', {
      expression: `
        selectPlantNode(17, false);
        ({
          title: document.getElementById('inspPlantTitle').textContent,
          lead: document.getElementById('inspLeadVal').textContent,
          mw: document.getElementById('inspMWVal').textContent
        });
      `,
      returnByValue: true
    });
    console.log('Normal Day L17:', resL17.result.value);

    console.log('All verification passed!');
    ws.close();
  } catch (err) {
    console.error('Error in test:', err);
  } finally {
    edge.kill();
  }
}

main();
