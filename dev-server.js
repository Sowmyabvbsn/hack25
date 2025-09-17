const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const mimeTypes = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

function getMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return mimeTypes[ext] || 'text/plain';
}

function serveFile(res, filePath) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 Not Found</h1>');
      return;
    }
    
    const mimeType = getMimeType(filePath);
    res.writeHead(200, { 
      'Content-Type': mimeType,
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    });
    res.end(data);
  });
}

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url);
  let pathname = parsedUrl.pathname;
  

  if (pathname === '/') {
    pathname = '/main.html';
  }
  if (pathname === '/ecom') {
    pathname = '/ecom.html';
  }
  if (pathname === '/index') {
    pathname = '/index.html';
  }
  
  const filePath = path.join(__dirname, pathname.substring(1));
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      if (pathname.endsWith('/')) {
        const indexPath = path.join(filePath, 'index.html');
        fs.access(indexPath, fs.constants.F_OK, (indexErr) => {
          if (indexErr) {
            res.writeHead(404, { 'Content-Type': 'text/html' });
            res.end('<h1>404 Not Found</h1>');
          } else {
            serveFile(res, indexPath);
          }
        });
      } else {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1>');
      }
    } else {
      // Check if it's a directory
      fs.stat(filePath, (statErr, stats) => {
        if (statErr) {
          res.writeHead(500, { 'Content-Type': 'text/html' });
          res.end('<h1>500 Internal Server Error</h1>');
          return;
        }
        
        if (stats.isDirectory()) {
          const indexPath = path.join(filePath, 'index.html');
          fs.access(indexPath, fs.constants.F_OK, (indexErr) => {
            if (indexErr) {
              res.writeHead(404, { 'Content-Type': 'text/html' });
              res.end('<h1>404 Not Found</h1>');
            } else {
              serveFile(res, indexPath);
            }
          });
        } else {
          serveFile(res, filePath);
        }
      });
    }
  });
});

const PORT = 8080;

server.listen(PORT, () => {
  console.log(`🚀 Development server running at: http://localhost:${PORT}`);
  console.log(`📱 Open your browser and navigate to: http://localhost:${PORT}/main.html`);
  console.log('Press Ctrl+C to stop the server');
  const open = (url) => {
    const { exec } = require('child_process');
    const command = process.platform === 'win32' ? 'start' : 
                   process.platform === 'darwin' ? 'open' : 'xdg-open';
    exec(`${command} ${url}`, (error) => {
      if (error) {
        console.log('Could not automatically open browser. Please open manually.');
      }
    });
  };
  setTimeout(() => {
    open(`http://localhost:${PORT}/main.html`);
  }, 1000);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use. Please try a different port or stop the other server.`);
  } else {
    console.error('Server error:', err);
  }
});

process.on('SIGINT', () => {
  console.log('\nShutting down development server...');
  server.close(() => {
    console.log('Development server stopped');
    process.exit(0);
  });
});

process.on('SIGTERM', () => {
  console.log('\nShutting down development server...');
  server.close(() => {
    console.log('Development server stopped');
    process.exit(0);
  });
});