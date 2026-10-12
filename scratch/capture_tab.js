// Script to interact with Edge via CDP and take screenshots of Tab 4
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function run() {
  const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
  const edge = spawn(edgePath, [
    '--headless=new',
    '--remote-debugging-port=9222',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    'http://localhost:8000/frontend/index.html'
  ]);

  console.log('Edge launched, waiting for CDP...');
  await new Promise(r => setTimeout(r, 2000));

  try {
    const listRes = await fetch('http://127.0.0.1:9222/json');
    const tabs = await listRes.json();
    console.log('Tabs:', tabs.map(t => ({ title: t.title, url: t.url })));

    const tab = tabs.find(t => t.url.includes('8000')) || tabs[0];
    if (!tab) {
      console.error('No tab found');
      return;
    }

    const ws = new WebSocket(tab.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => {
      ws.onopen = resolve;
      ws.onerror = reject;
    });

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

    // Set viewport
    await send('Emulation.setDeviceMetricsOverride', {
      width: 1440,
      height: 1200,
      deviceScaleFactor: 1,
      mobile: false
    });

    // Wait for page to finish loading data
    await new Promise(r => setTimeout(r, 2000));

    // Click Tab 4
    const evalRes = await send('Runtime.evaluate', {
      expression: `
        (function() {
          const tab = document.getElementById('tabMap');
          if (tab) {
            tab.click();
            return { success: true, active: tab.classList.contains('active') };
          }
          return { success: false };
        })()
      `,
      returnByValue: true
    });
    console.log('Click Tab 4 result:', evalRes.result.value);

    // Wait for canvas & charts to render
    await new Promise(r => setTimeout(r, 1500));

    // Capture screenshot of the top half (Strategic Doctrine + Radar Console)
    const ss1 = await send('Page.captureScreenshot', { format: 'png' });
    const ssPath1 = path.join(__dirname, 'cloud_radar_feature_top.png');
    fs.writeFileSync(ssPath1, Buffer.from(ss1.data, 'base64'));
    console.log('Saved top screenshot to:', ssPath1);

    // Test scenario click (Cold Front Storm)
    const scenRes = await send('Runtime.evaluate', {
      expression: `
        (function() {
          setCloudScenario('fast');
          return { scenario: currentRadarScenario };
        })()
      `,
      returnByValue: true
    });
    console.log('Set scenario result:', scenRes.result.value);
    await new Promise(r => setTimeout(r, 800));

    // Scroll down to Split Charts and Matrix
    await send('Runtime.evaluate', {
      expression: `window.scrollTo(0, 750);`
    });
    await new Promise(r => setTimeout(r, 800));

    // Capture screenshot of the bottom half (Split Charts & Empirical Matrix)
    const ss2 = await send('Page.captureScreenshot', { format: 'png' });
    const ssPath2 = path.join(__dirname, 'cloud_radar_feature_charts.png');
    fs.writeFileSync(ssPath2, Buffer.from(ss2.data, 'base64'));
    console.log('Saved charts screenshot to:', ssPath2);

    // Check console errors
    const errorsRes = await send('Runtime.evaluate', {
      expression: `window.__consoleErrors || []`,
      returnByValue: true
    });
    console.log('Console errors:', errorsRes.result.value);

    ws.close();
  } catch (err) {
    console.error('CDP Error:', err);
  } finally {
    edge.kill();
  }
}

run();
