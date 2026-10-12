const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('frontend/index.html', 'utf8');

// Extract all <script> contents (excluding external ones)
const scriptRegex = /<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let scriptIdx = 0;

// Mock minimum browser globals for syntax verification
const sandbox = {
  window: {},
  document: {
    getElementById: () => ({ addEventListener: () => {}, classList: { add: () => {}, remove: () => {} }, style: {} }),
    querySelectorAll: () => [],
    addEventListener: () => {}
  },
  console: console,
  Chart: function() {},
  Papa: { parse: () => {}, unparse: () => '' },
  gsap: { fromTo: () => {}, to: () => {} },
  Date: Date,
  Math: Math,
  parseFloat: parseFloat,
  parseInt: parseInt,
  requestAnimationFrame: () => 1
};

while ((match = scriptRegex.exec(html)) !== null) {
  scriptIdx++;
  const code = match[1];
  try {
    const script = new vm.Script(code, { filename: `inline-script-${scriptIdx}.js` });
    console.log(`Script ${scriptIdx} parsed without syntax errors (${code.length} chars).`);
  } catch (err) {
    console.error(`Syntax error in script ${scriptIdx}:`, err);
    process.exit(1);
  }
}

console.log('ALL INLINE SCRIPTS ARE 100% SYNTACTICALLY VALID!');
