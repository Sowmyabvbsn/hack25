const { spawn, exec } = require('child_process');

console.log('Starting development server...');

const server = spawn('npx', ['http-server', '.', '-p', '8080', '-o', '/main.html'], {
  stdio: 'inherit'
});

server.on('error', (err) => {
  console.error('Failed to start development server:', err);
  console.log('Make sure http-server is installed: npm install http-server --save-dev');
});

server.on('close', (code) => {
  console.log(`Development server exited with code ${code}`);
});

process.on('SIGINT', () => {
  console.log('\nShutting down development server...');
  server.kill();
  process.exit();
});

process.on('SIGTERM', () => {
  console.log('\nShutting down development server...');
  server.kill();
  process.exit();
});