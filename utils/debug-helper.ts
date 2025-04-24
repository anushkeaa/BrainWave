// Debug helper utility to diagnose backend connection issues

// Log with timestamp and category
export const logWithTimestamp = (category: string, message: string, data?: any) => {
  const timestamp = new Date().toISOString().split('T')[1].split('.')[0]; // HH:MM:SS
  console.log(`[${timestamp}] [${category}] ${message}`, data || '');
};

// Debug network connectivity
export const debugNetworkConnectivity = async () => {
  logWithTimestamp('DEBUG', 'Testing network connectivity...');
  
  try {
    // Test general internet connectivity
    const internetTest = await fetch('https://www.google.com/favicon.ico', {
      method: 'HEAD',
      mode: 'no-cors',
      cache: 'no-store'
    });
    logWithTimestamp('DEBUG', 'Internet connectivity: OK');
  } catch (error) {
    logWithTimestamp('DEBUG', 'Internet connectivity: FAILED', error);
  }
  
  // Test local connections
  const localHosts = ['localhost', '127.0.0.1'];
  const ports = [5000, 8000, 3000, 8080];
  
  for (const host of localHosts) {
    for (const port of ports) {
      const url = `http://${host}:${port}`;
      try {
        logWithTimestamp('DEBUG', `Testing connection to ${url}...`);
        const response = await fetch(url, {
          method: 'GET',
          mode: 'cors',
          cache: 'no-store',
          signal: AbortSignal.timeout(2000)
        });
        
        logWithTimestamp('DEBUG', `Connection to ${url}: ${response.status} ${response.statusText}`);
        
        // If successful, try to get response body
        if (response.ok) {
          try {
            const text = await response.text();
            logWithTimestamp('DEBUG', `Response from ${url}:`, text.substring(0, 200) + (text.length > 200 ? '...' : ''));
          } catch (e) {
            logWithTimestamp('DEBUG', `Could not read response from ${url}:`, e);
          }
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          logWithTimestamp('DEBUG', `Connection to ${url}: TIMEOUT`);
        } else {
          logWithTimestamp('DEBUG', `Connection to ${url}: FAILED`, error);
        }
      }
    }
  }
  
  // Show user agent and browser details
  logWithTimestamp('DEBUG', 'Browser details:', {
    userAgent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    vendor: navigator.vendor
  });
  
  // Check browser features
  logWithTimestamp('DEBUG', 'Browser features:', {
    cors: typeof window.fetch === 'function',
    webSockets: typeof WebSocket === 'function',
    localStorage: typeof localStorage === 'object',
    abortController: typeof AbortController === 'function',
    sharedWorker: typeof SharedWorker === 'function'
  });
  
  return 'Debug information logged to console. Press F12 to view.';
};

// Add a global debugging function that can be called from the browser console
// @ts-ignore
window.debugBrainwaveApp = () => {
  logWithTimestamp('MANUAL-DEBUG', 'Manual debug triggered');
  return debugNetworkConnectivity();
};

// Initialize debug tools
export const initDebugTools = () => {
  logWithTimestamp('INIT', 'Initializing debug tools...');
  
  // Add error tracking
  const originalConsoleError = console.error;
  console.error = (...args: any[]) => {
    // Log to original console.error
    originalConsoleError.apply(console, args);
    
    // Add to error log in localStorage for later retrieval
    try {
      const errorLog = JSON.parse(localStorage.getItem('bw_error_log') || '[]');
      errorLog.push({
        timestamp: new Date().toISOString(),
        error: args.map(arg => 
          arg instanceof Error 
            ? { name: arg.name, message: arg.message, stack: arg.stack } 
            : String(arg)
        )
      });
      
      // Keep only the last 50 errors
      if (errorLog.length > 50) {
        errorLog.shift();
      }
      
      localStorage.setItem('bw_error_log', JSON.stringify(errorLog));
    } catch (e) {
      // Ignore errors in error logging
    }
  };
  
  // Log initialization complete
  logWithTimestamp('INIT', 'Debug tools initialized');
  
  // Return a function to view the error log
  // @ts-ignore
  window.viewBrainwaveErrorLog = () => {
    try {
      return JSON.parse(localStorage.getItem('bw_error_log') || '[]');
    } catch (e) {
      return 'Error reading log';
    }
  };
};

// Export a helper to run comprehensive diagnostics
export const runComprehensiveDiagnostics = async () => {
  logWithTimestamp('DIAGNOSTICS', 'Running comprehensive diagnostics...');
  
  // Test network connectivity
  await debugNetworkConnectivity();
  
  // Test storage
  try {
    localStorage.setItem('bw_test', 'test');
    localStorage.removeItem('bw_test');
    logWithTimestamp('DIAGNOSTICS', 'LocalStorage: OK');
  } catch (e) {
    logWithTimestamp('DIAGNOSTICS', 'LocalStorage: FAILED', e);
  }
  
  // Report on window.location
  logWithTimestamp('DIAGNOSTICS', 'Current location:', {
    href: window.location.href,
    protocol: window.location.protocol,
    host: window.location.host,
    pathname: window.location.pathname
  });
  
  // Show any query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const paramObj: Record<string, string> = {};
  urlParams.forEach((value, key) => {
    paramObj[key] = value;
  });
  
  if (Object.keys(paramObj).length > 0) {
    logWithTimestamp('DIAGNOSTICS', 'URL Parameters:', paramObj);
  }
  
  logWithTimestamp('DIAGNOSTICS', 'Diagnostics complete');
  return 'Diagnostics complete. Check console for results.';
};

// Initialize debug tools
initDebugTools();
