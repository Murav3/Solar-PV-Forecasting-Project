const { spawn } = require('child_process');

async function test() {
  const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
  const edge = spawn(edgePath, [
    '--headless=new',
    '--remote-debugging-port=9222',
    '--disable-gpu',
    'http://localhost:8000/frontend/index.html'
  ]);

  await new Promise(r => setTimeout(r, 2000));

  try {
    const listRes = await fetch('http://127.0.0.1:9222/json');
    const tabs = await listRes.json();
    const tab = tabs.find(t => t.url.includes('8000'));
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

    ws.onmessage = (evt) => {
      const data = JSON.parse(evt.data);
      if (data.method === 'Runtime.exceptionThrown') {
        console.error('EXCEPTION THROWN:', JSON.stringify(data.params.exceptionDetails));
      }
      if (data.method === 'Runtime.consoleAPICalled') {
        console.log('CONSOLE LOG:', data.params.type, data.params.args);
      }
    };

    await send('Runtime.enable');
    await send('Log.enable');

    // Wait 2 sec
    await new Promise(r => setTimeout(r, 2000));

    console.log('Clicking tabMap and calling drawTacticalRadarCanvas with try/catch...');
    const res = await send('Runtime.evaluate', {
      expression: `
        (function() {
          try {
            switchTab('map');
            return 'SWITCHED OK';
          } catch(e) {
            return 'ERROR IN SWITCHTAB: ' + e.stack;
          }
        })()
      `,
      returnByValue: true
    });
    console.log('switchTab eval result:', res.result.value);

    // Now test drawTacticalRadarCanvas specifically
    const drawRes = await send('Runtime.evaluate', {
      expression: `
        (function() {
          try {
            drawTacticalRadarCanvas();
            return 'DRAW OK';
          } catch(e) {
            return 'ERROR IN DRAW: ' + e.stack;
          }
        })()
      `,
      returnByValue: true
    });
    console.log('drawTacticalRadarCanvas eval result:', drawRes.result.value);

    ws.close();
  } catch (err) {
    console.error(err);
  } finally {
    edge.kill();
  }
}

test();
