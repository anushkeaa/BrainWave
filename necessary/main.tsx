import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Simple error boundary for the entire app
class ErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean, error: Error | null}> {
  constructor(props: {children: React.ReactNode}) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("React Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', fontFamily: 'system-ui' }}>
          <h1 style={{ color: '#e63946' }}>Something went wrong</h1>
          <div style={{ padding: '15px', background: '#f8f9fa', borderRadius: '4px', marginTop: '15px' }}>
            <p><strong>Error: </strong>{this.state.error?.message || 'Unknown error'}</p>
            <p>Try refreshing the page or check the console for more details.</p>
          </div>
          <button 
            onClick={() => window.location.reload()} 
            style={{ 
              marginTop: '15px', 
              padding: '8px 16px', 
              background: '#3a86ff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Refresh Page
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
);
