const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');

// Find all script tags
const scriptRegex = /<script\b[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let scriptIndex = 0;

while ((match = scriptRegex.exec(html)) !== null) {
  scriptIndex++;
  const scriptContent = match[1];
  if (!scriptContent.trim()) continue;
  
  console.log(`Checking script #${scriptIndex} (length: ${scriptContent.length} chars)...`);
  try {
    new Function(scriptContent);
    console.log(`Script #${scriptIndex}: SYNTAX VALID!`);
  } catch (err) {
    console.error(`Script #${scriptIndex} SYNTAX ERROR:`, err.message);
    // Find line number
    const lines = scriptContent.split('\n');
    console.error('Stack:', err.stack);
  }
}
