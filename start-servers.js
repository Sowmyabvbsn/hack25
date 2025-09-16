const { spawn } = require('child_process');
const path = require('path');

console.log('Starting backend server...');
const backend = spawn('node', ['server.js'], {
  cwd: path.join(__dirname, 'QUIZB', 'backendQ'),
  stdio: 'inherit'
});

backend.on('error', (err) => {
  console.error('Failed to start backend server:', err);
});

backend.on('close', (code) => {
  console.log(`Backend server exited with code ${code}`);
});
process.on('SIGINT', () => {
  console.log('\nShutting down servers...');
  backend.kill();
  process.exit();
});

process.on('SIGTERM', () => {
  console.log('\nShutting down servers...');
  backend.kill();
  process.exit();
});