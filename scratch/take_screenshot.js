const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

async function main() {
  const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
  const profileDir = path.join(__dirname, 'fresh_profile_radar');
  
  const edge = spawn(edgePath, [
    '--headless=new',
    '--remote-debugging-port=9333',
    `--user-data-dir=${profileDir}`,
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    `http://localhost:8000/frontend/index.html?v=${Date.now()}`
  ]);

  console.log('Launched Edge on port 9333...');
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
      height: 1150,
      deviceScaleFactor: 1,
      mobile: false
    });

    await new Promise(r => setTimeout(r, 2000));

    // 1. Verify Tab 1 (Fleet Overview) is 100% intact
    console.log('Verifying Tab 1 intact...');
    const ssFleet = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(__dirname, 'fleet_overview_unchanged.png'), Buffer.from(ssFleet.data, 'base64'));

    // 2. Switch to Tab 4 (Map & Radar)
    console.log('Switching to Tab 4...');
    await send('Runtime.evaluate', { expression: `switchTab('map');` });
    await new Promise(r => setTimeout(r, 1200));

    // Scroll to radar console
    await send('Runtime.evaluate', { expression: `window.scrollTo(0, 320);` });
    await new Promise(r => setTimeout(r, 600));

    // Screenshot 1: Clean radar map with L13 selected by default
    console.log('Capturing clean radar map...');
    const ssCleanMap = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(__dirname, 'radar_clean_map.png'), Buffer.from(ssCleanMap.data, 'base64'));

    // 3. Test interactivity: Select Plant L5
    console.log('Selecting Plant L5 (Array B1)...');
    await send('Runtime.evaluate', {
      expression: `
        selectPlantNode(5, true);
      `
    });
    await new Promise(r => setTimeout(r, 800));

    const ssL5 = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(__dirname, 'radar_interactive_plant_l5.png'), Buffer.from(ssL5.data, 'base64'));

    // 4. Test Simulation Scrubber and Cloud Movement
    console.log('Simulating cloud movement (scrubber at 65%)...');
    await send('Runtime.evaluate', {
      expression: `
        onRadarScrubber(65);
      `
    });
    await new Promise(r => setTimeout(r, 800));

    const ssSim = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(path.join(__dirname, 'radar_sim_scrubbed.png'), Buffer.from(ssSim.data, 'base64'));

    console.log('All verification screenshots saved successfully!');
    ws.close();
  } catch (err) {
    console.error('Error in main:', err);
  } finally {
    edge.kill();
  }
}

main();
