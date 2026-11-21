const fs = require('node:fs');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, 'entry.png'));
const outputDirectory = process.env.MAKEFUN_OUTPUT_DIR || '/output';

fs.mkdirSync(outputDirectory, { recursive: true });
for (const name of fs.readdirSync(outputDirectory)) {
  fs.rmSync(path.join(outputDirectory, name), { recursive: true, force: true });
}
fs.writeFileSync(path.join(outputDirectory, 'entry.png'), source);
