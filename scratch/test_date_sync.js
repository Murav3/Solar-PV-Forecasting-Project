const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function main() {
  const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
  const profileDir = path.join(__dirname, 'fresh_profile_dates');
  
  const edge = spawn(edgePath, [
    '--headless=new',
    '--remote-debugging-port=9444',
    `--user-data-dir=${profileDir}`,
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    `http://localhost:8000/frontend/index.html?v=${Date.now()}`
  ]);

  console.log('Launched Edge on port 9444...');
  await new Promise(r => setTimeout(r, 2500));

  try {
    const listRes = await fetch('http://127.0.0.1:9444/json');
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

    // Wait for data load
    await new Promise(r => setTimeout(r, 2000));

    // Switch to Tab 4
    console.log('Switching to Tab 4...');
    await send('Runtime.evaluate', {
      expression: `switchTab('map');`
    });
    await new Promise(r => setTimeout(r, 1000));

    // Test changing to a different date (e.g., date index 10)
    console.log('Changing date in dropdown...');
    await send('Runtime.evaluate', {
      expression: `
        (function() {
          const sel = document.getElementById('dateSelect');
          if (sel && sel.options.length > 10) {
            sel.selectedIndex = 10;
            onDateSelectChange();
            return { newDate: sel.value };
          }
          return { error: 'not enough dates' };
        })()
      `
    });
    await new Promise(r => setTimeout(r, 800));

    // Click Replay Selected Date Transients button
    console.log('Clicking Replay Selected Date button...');
    await send('Runtime.evaluate', {
      expression: `setCloudScenario('dateSpecific');`
    });
    await new Promise(r => setTimeout(r, 1000));

    // Capture screenshot of Top Half
    const ss1 = await send('Page.captureScreenshot', { format: 'png' });
    const p1 = path.join(__dirname, 'us_radar_date_synced_top.png');
    fs.writeFileSync(p1, Buffer.from(ss1.data, 'base64'));
    console.log('Saved date synced top screenshot to:', p1);

    ws.close();
  } catch (err) {
    console.error('Error:', err);
  } finally {
    edge.kill();
  }
}

main();
