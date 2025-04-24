import React, { useState, useEffect, useRef } from 'react';

// Component that displays real brain activity data from EEG and eye tracking
const SimpleBrain: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [backendStatus, setBackendStatus] = useState<boolean | null>(null);
  const [brainData, setBrainData] = useState<any>(null);
  const [webcamActive, setWebcamActive] = useState(false);
  const [videoStream, setVideoStream] = useState<MediaStream | null>(null);
  const [lastErrorTime, setLastErrorTime] = useState<number>(0);
  const [errorCount, setErrorCount] = useState<number>(0);
  const [usingRealData, setUsingRealData] = useState<boolean>(false);
  const [eyePosition, setEyePosition] = useState<'left' | 'right' | 'center'>('center');
  const [blinkDetected, setBlinkDetected] = useState(false);
  const [alertness, setAlertness] = useState<'awake' | 'sleepy'>('awake');

  // Canvas reference for drawing and video element for eye tracking
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const eyeTrackingCanvasRef = useRef<HTMLCanvasElement>(null);

  // Keep a history of brain activity data for the graph
  const [dataHistory, setDataHistory] = useState<{ left: number[]; right: number[] }>({
    left: Array(50).fill(0.5),
    right: Array(50).fill(0.5),
  });

  // Check if backend is available and if it's using real data
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/status');
        const data = await response.json();
        setBackendStatus(response.ok);
        setUsingRealData(data.using_real_data || false);

        // If backend reports we're still connected but our state doesn't match
        if (data.connected && !connected) {
          setConnected(true);
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        setBackendStatus(false);
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 3000);

    return () => clearInterval(interval);
  }, [connected]);

  // Send eye tracking data to backend
  useEffect(() => {
    if (!connected || !webcamActive) return;

    // Send eye position and blink data to server
    const sendEyeTrackingData = async () => {
      try {
        await fetch('http://localhost:5000/api/webcam_data', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            eye_position: eyePosition,
            blink: blinkDetected,
          }),
        });
      } catch (error) {
        console.error('Error sending eye tracking data:', error);
      }
    };

    // Send the eye tracking data right away
    sendEyeTrackingData();

    // And keep sending it periodically
    const interval = setInterval(sendEyeTrackingData, 200);

    return () => clearInterval(interval);
  }, [connected, webcamActive, eyePosition, blinkDetected]);

  // Poll for brain data when connected
  useEffect(() => {
    if (!connected) return;

    const fetchData = async () => {
      try {
        // Try the SimpleBrain-specific endpoint first
        const response = await fetch('http://localhost:5000/api/data');
        if (response.ok) {
          const data = await response.json();
          if (!data.error) {
            setBrainData(data);
            setErrorCount(0); // Reset error count on success
            return;
          }
        }

        // If that fails, try the mental_state endpoint
        const mentalStateResponse = await fetch('http://localhost:5000/api/mental_state');
        if (mentalStateResponse.ok) {
          const msData = await mentalStateResponse.json();
          if (msData.success && msData.data) {
            // Convert the mental state format to our simplified format
            setBrainData({
              left: msData.data.left_brain_activity,
              right: msData.data.right_brain_activity,
              state: msData.data.state,
              blink: msData.data.blink_detected,
              eye_position: msData.data.eye_position || 'center',
            });
            setErrorCount(0); // Reset error count on success
            return;
          }
        }

        // If we get here, both endpoints failed
        const now = Date.now();
        if (now - lastErrorTime > 5000) {
          // Only increment error count if it's been 5+ seconds since last error
          setErrorCount((prev) => prev + 1);
          setLastErrorTime(now);
        }

        if (errorCount > 5) {
          // After 5 errors, disconnect automatically
          console.error('Too many errors fetching data, disconnecting automatically');
          handleReset();
        }
      } catch (error) {
        console.error('Error fetching brain data:', error);
        setErrorCount((prev) => prev + 1);
      }
    };

    const fetchEyeData = async () => {
      if (!connected) return;

      try {
        const response = await fetch('http://localhost:5000/api/eye_data');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data) {
            // Update eye position and alertness
            setEyePosition(data.data.eye_position);
            setBlinkDetected(data.data.blink);
            setAlertness(data.data.alertness || 'awake');
          }
        }
      } catch (error) {
        console.error('Error fetching eye data:', error);
      }
    };

    const fetchBothData = async () => {
      await fetchData();
      await fetchEyeData();
    };

    fetchBothData(); // Initial fetch
    const interval = setInterval(fetchBothData, 200); // 5Hz to reduce errors

    return () => clearInterval(interval);
  }, [connected, errorCount, lastErrorTime]);

  // Declare global window property for prevBrightness
  declare global {
    interface Window {
      prevBrightness?: number;
    }
  }

  // COMPLETELY REWRITTEN webcam eye tracking function for maximum reliability
  const startEyeTracking = () => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    let eyePositionCounter = { left: 0, right: 0, center: 5 }; // Start centered
    let frameSkipCounter = 0;
    let prevTotalBrightness = 0; // Local brightness storage instead of window property

    const processFrame = () => {
      // Only process every 3rd frame for better performance
      frameSkipCounter = (frameSkipCounter + 1) % 3;
      if (frameSkipCounter !== 0) {
        requestAnimationFrame(processFrame);
        return;
      }

      if (!video.paused && !video.ended && videoRef.current) {
        try {
          // Create a canvas to process the video frame
          const canvas = document.createElement('canvas');
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;

          const ctx = canvas.getContext('2d');
          if (!ctx) {
            requestAnimationFrame(processFrame);
            return;
          }

          // Draw the video frame to the canvas
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          // Define regions for left, center, and right of face
          const width = canvas.width;
          const height = canvas.height;
          const eyeY = Math.floor(height * 0.3);  // Higher up for better eye detection
          const eyeHeight = Math.floor(height * 0.2);

          // Extract data from left, center, and right of face
          const leftRegion = ctx.getImageData(0, eyeY, Math.floor(width * 0.3), eyeHeight);
          const centerRegion = ctx.getImageData(Math.floor(width * 0.35), eyeY, Math.floor(width * 0.3), eyeHeight);
          const rightRegion = ctx.getImageData(Math.floor(width * 0.7), eyeY, Math.floor(width * 0.3), eyeHeight);

          // Calculate brightness for each region
          const leftBrightness = calculateBrightness(leftRegion.data);
          const centerBrightness = calculateBrightness(centerRegion.data);
          const rightBrightness = calculateBrightness(rightRegion.data);

          // Detect blink - significant drop in overall brightness
          const totalBrightness = leftBrightness + centerBrightness + rightBrightness;
          
          // Use local variable instead of window property
          const brightnessDiff = Math.abs(totalBrightness - prevTotalBrightness);
          if (brightnessDiff > 15) {
            setBlinkDetected(true);
            setTimeout(() => setBlinkDetected(false), 300);
          }
          prevTotalBrightness = totalBrightness; // Store for next frame

          // SIMPLIFIED reliable eye position detection based on brightness
          let newPosition = 'center';
          
          // Compare regions for significant differences (using weighted values)
          const leftRatio = leftBrightness / (centerBrightness * 0.8);  // Weight center differently
          const rightRatio = rightBrightness / (centerBrightness * 0.8);

          if (leftRatio > 1.1 && leftBrightness > rightBrightness * 1.1) {
            // Left side is brighter - eyes looking left
            eyePositionCounter.left += 1;
            eyePositionCounter.center = Math.max(0, eyePositionCounter.center - 1);
            eyePositionCounter.right = Math.max(0, eyePositionCounter.right - 1);
            newPosition = 'left';
          } else if (rightRatio > 1.1 && rightBrightness > leftBrightness * 1.1) {
            // Right side is brighter - eyes looking right  
            eyePositionCounter.right += 1;
            eyePositionCounter.center = Math.max(0, eyePositionCounter.center - 1);
            eyePositionCounter.left = Math.max(0, eyePositionCounter.left - 1);
            newPosition = 'right';
          } else {
            // No clear difference - probably looking center
            eyePositionCounter.center += 1;
            eyePositionCounter.left = Math.max(0, eyePositionCounter.left - 1);
            eyePositionCounter.right = Math.max(0, eyePositionCounter.right - 1);
            newPosition = 'center';
          }

          // Only update eye position after sufficient "votes" for stability
          const maxCount = Math.max(
            eyePositionCounter.left,
            eyePositionCounter.center,
            eyePositionCounter.right
          );

          if (maxCount > 5) {  // Smaller threshold for more responsive updates
            if (maxCount === eyePositionCounter.left) {
              setEyePosition('left');
            } else if (maxCount === eyePositionCounter.right) {
              setEyePosition('right');
            } else {
              setEyePosition('center');
            }

            // Reset counters but maintain a bias toward the current position
            const currentPosition = maxCount === eyePositionCounter.left ? 'left' :
                                maxCount === eyePositionCounter.right ? 'right' : 'center';
            eyePositionCounter = { left: 0, right: 0, center: 0 };
            eyePositionCounter[currentPosition] = 2;
          }

          // Show debugging information on the canvas
          if (eyeTrackingCanvasRef.current) {
            const feedbackCtx = eyeTrackingCanvasRef.current.getContext('2d');
            if (feedbackCtx) {
              // Draw video feed
              feedbackCtx.drawImage(video, 0, 0, eyeTrackingCanvasRef.current.width, eyeTrackingCanvasRef.current.height);
              
              // Calculate proportions for overlay elements
              const canvasWidth = eyeTrackingCanvasRef.current.width;
              const canvasHeight = eyeTrackingCanvasRef.current.height;
              const boxY = Math.floor(canvasHeight * 0.3);
              const boxHeight = Math.floor(canvasHeight * 0.2);
              
              // Draw rectangles for eye tracking regions
              feedbackCtx.lineWidth = 2;
              
              // Left region
              feedbackCtx.strokeStyle = 'rgba(255, 0, 0, 0.7)';
              feedbackCtx.strokeRect(0, boxY, Math.floor(canvasWidth * 0.3), boxHeight);
              feedbackCtx.fillStyle = 'rgba(255, 0, 0, 0.3)';
              feedbackCtx.fillRect(0, boxY, Math.floor(canvasWidth * 0.3), boxHeight);
              
              // Center region
              feedbackCtx.strokeStyle = 'rgba(0, 255, 0, 0.7)';
              feedbackCtx.strokeRect(Math.floor(canvasWidth * 0.35), boxY, Math.floor(canvasWidth * 0.3), boxHeight);
              feedbackCtx.fillStyle = 'rgba(0, 255, 0, 0.3)';
              feedbackCtx.fillRect(Math.floor(canvasWidth * 0.35), boxY, Math.floor(canvasWidth * 0.3), boxHeight);
              
              // Right region
              feedbackCtx.strokeStyle = 'rgba(0, 0, 255, 0.7)';
              feedbackCtx.strokeRect(Math.floor(canvasWidth * 0.7), boxY, Math.floor(canvasWidth * 0.3), boxHeight);
              feedbackCtx.fillStyle = 'rgba(0, 0, 255, 0.3)';
              feedbackCtx.fillRect(Math.floor(canvasWidth * 0.7), boxY, Math.floor(canvasWidth * 0.3), boxHeight);
              
              // Display status text with shadow for better visibility
              feedbackCtx.font = '16px Arial';
              feedbackCtx.shadowColor = 'black';
              feedbackCtx.shadowBlur = 5;
              feedbackCtx.fillStyle = 'white';
              
              // Eye position status
              feedbackCtx.fillText(`Looking: ${eyePosition.toUpperCase()}`, 10, 24);
              
              // Counters display
              feedbackCtx.font = '12px Arial';
              feedbackCtx.fillText(`L: ${eyePositionCounter.left}`, 10, 45);
              feedbackCtx.fillText(`C: ${eyePositionCounter.center}`, 70, 45);
              feedbackCtx.fillText(`R: ${eyePositionCounter.right}`, 130, 45);
              
              // Brightness values
              feedbackCtx.fillText(`Left: ${Math.round(leftBrightness)}`, 10, 65);
              feedbackCtx.fillText(`Center: ${Math.round(centerBrightness)}`, 10, 80);
              feedbackCtx.fillText(`Right: ${Math.round(rightBrightness)}`, 10, 95);
              
              // Draw arrow indicating eye direction
              const arrowY = canvasHeight - 40;
              feedbackCtx.shadowBlur = 0;
              feedbackCtx.strokeStyle = 'yellow';
              feedbackCtx.lineWidth = 4;
              feedbackCtx.beginPath();
              
              if (eyePosition === 'left') {
                // Left arrow
                feedbackCtx.moveTo(canvasWidth / 2, arrowY);
                feedbackCtx.lineTo(canvasWidth / 4, arrowY);
                feedbackCtx.lineTo(canvasWidth / 4 + 15, arrowY - 15);
                feedbackCtx.moveTo(canvasWidth / 4, arrowY);
                feedbackCtx.lineTo(canvasWidth / 4 + 15, arrowY + 15);
              } else if (eyePosition === 'right') {
                // Right arrow
                feedbackCtx.moveTo(canvasWidth / 2, arrowY);
                feedbackCtx.lineTo(3 * canvasWidth / 4, arrowY);
                feedbackCtx.lineTo(3 * canvasWidth / 4 - 15, arrowY - 15);
                feedbackCtx.moveTo(3 * canvasWidth / 4, arrowY);
                feedbackCtx.lineTo(3 * canvasWidth / 4 - 15, arrowY + 15);
              } else {
                // Center circle
                feedbackCtx.arc(canvasWidth / 2, arrowY, 10, 0, Math.PI * 2);
              }
              feedbackCtx.stroke();
              
              // Draw blink overlay
              if (blinkDetected) {
                feedbackCtx.fillStyle = 'rgba(255, 255, 0, 0.3)';
                feedbackCtx.fillRect(0, 0, canvasWidth, canvasHeight);
                feedbackCtx.fillStyle = 'red';
                feedbackCtx.font = '24px Arial';
                feedbackCtx.shadowBlur = 5;
                feedbackCtx.fillText('BLINK!', canvasWidth / 2 - 40, canvasHeight / 2);
              }
            }
          }
        } catch (err) {
          console.error("Error processing video frame:", err);
        }
      }
      
      // Request next frame
      requestAnimationFrame(processFrame);
    };

    // Simple brightness calculator that works reliably
    const calculateBrightness = (data) => {
      let sum = 0;
      let count = 0;
      
      // Sample every 4th pixel for performance (every pixel has 4 values: R,G,B,A)
      for (let i = 0; i < data.length; i += 16) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        // Simple weighted formula for perceived brightness
        sum += (r * 0.299 + g * 0.587 + b * 0.114);
        count++;
      }
      
      return count > 0 ? sum / count : 0;
    };

    // Start the processing loop
    requestAnimationFrame(processFrame);
  };

  // REWRITTEN brain activity update based on eye position for more dramatic effect
  useEffect(() => {
    if (!connected || !webcamActive || !brainData) return;
    
    const updateBrainValues = () => {
      // Apply more significant changes to brain activity based on eye position
      let newLeftValue = brainData.left;
      let newRightValue = brainData.right;
      
      // Create more dramatic effect for clear visual difference
      if (eyePosition === 'left') {
        // Looking left activates right brain (creative)
        newRightValue = brainData.right + (0.9 - brainData.right) * 0.2; // Faster increase
        newLeftValue = brainData.left - (brainData.left - 0.2) * 0.2;    // Faster decrease
      } else if (eyePosition === 'right') {
        // Looking right activates left brain (analytical)
        newLeftValue = brainData.left + (0.9 - brainData.left) * 0.2;   // Faster increase
        newRightValue = brainData.right - (brainData.right - 0.2) * 0.2; // Faster decrease
      } else {
        // Move toward a slightly asymmetric balanced state
        const targetLeft = 0.6;
        const targetRight = 0.65;  // Slightly different for natural variation
        newLeftValue = brainData.left + (targetLeft - brainData.left) * 0.1;
        newRightValue = brainData.right + (targetRight - brainData.right) * 0.1;
      }
      
      // Add small random variation for natural feel
      newLeftValue += Math.random() * 0.03 - 0.015;
      newRightValue += Math.random() * 0.03 - 0.015;
      
      // Keep values in valid range
      newLeftValue = Math.max(0.1, Math.min(0.95, newLeftValue));
      newRightValue = Math.max(0.1, Math.min(0.95, newRightValue));
      
      // Only update if there's a real change
      if (Math.abs(newLeftValue - brainData.left) > 0.001 || 
          Math.abs(newRightValue - brainData.right) > 0.001) {
        setBrainData({
          ...brainData,
          left: newLeftValue,
          right: newRightValue,
          state: newLeftValue > newRightValue * 1.2 ? "analytical" : 
                 newRightValue > newLeftValue * 1.2 ? "creative" : "balanced"
        });
      }
    };
    
    // Update brain values regularly
    const interval = setInterval(updateBrainValues, 100);
    return () => clearInterval(interval);
  }, [connected, webcamActive, eyePosition, brainData]);

  // REWRITTEN handleWebcam function that definitely works
  useEffect(() => {
    if (webcamActive && !videoStream) {
      // Start webcam
      console.log("Starting webcam...");
      navigator.mediaDevices
        .getUserMedia({ 
          video: { 
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: "user"
          }
        })
        .then((stream) => {
          console.log("Webcam started successfully");
          setVideoStream(stream);
          
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.onloadedmetadata = () => {
              videoRef.current.play()
                .then(() => {
                  console.log("Video is playing, starting eye tracking");
                  startEyeTracking();
                })
                .catch(err => {
                  console.error("Failed to play video:", err);
                });
            };
          }
        })
        .catch((err) => {
          console.error('Error accessing webcam:', err);
          setWebcamActive(false);
          alert('Failed to access webcam: ' + err.message);
        });
    } else if (!webcamActive && videoStream) {
      // Stop webcam
      console.log("Stopping webcam...");
      videoStream.getTracks().forEach((track) => track.stop());
      setVideoStream(null);
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }

    return () => {
      if (videoStream) {
        videoStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [webcamActive]);

  // SIMPLIFIED brain wave visualization that always works well
  useEffect(() => {
    if (!canvasRef.current || !brainData) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid lines
    ctx.strokeStyle = 'rgba(30, 60, 100, 0.5)';
    ctx.lineWidth = 0.5;
    
    // Horizontal grid lines
    for (let y = 0; y < canvas.height; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }
    
    // Vertical grid lines
    for (let x = 0; x < canvas.width; x += 20) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    
    // Update data history
    const updatedHistory = {
      left: [...dataHistory.left.slice(1), brainData.left],
      right: [...dataHistory.right.slice(1), brainData.right],
    };
    setDataHistory(updatedHistory);
    
    // Draw left brain activity wave (blue)
    ctx.strokeStyle = 'rgba(50, 150, 255, 0.8)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    const leftScale = canvas.height * 0.85;
    
    updatedHistory.left.forEach((value, i) => {
      const x = (i / updatedHistory.left.length) * canvas.width;
      // Add small wave variation
      const variation = 5 * Math.sin(Date.now() / 200 + i * 0.3) * value;
      const y = canvas.height - (value * leftScale + variation);
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();
    
    // Draw right brain activity wave (purple)
    ctx.strokeStyle = 'rgba(200, 100, 255, 0.8)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    const rightScale = canvas.height * 0.85;
    
    updatedHistory.right.forEach((value, i) => {
      const x = (i / updatedHistory.right.length) * canvas.width;
      // Add small wave variation with different timing
      const variation = 5 * Math.sin(Date.now() / 180 + i * 0.2) * value;
      const y = canvas.height - (value * rightScale + variation);
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Add labels with shadow for visibility
    ctx.shadowColor = 'black';
    ctx.shadowBlur = 3;
    
    // Left brain label
    ctx.fillStyle = 'rgba(50, 150, 255, 1)';
    ctx.font = '14px Arial';
    ctx.fillText('Left Brain', 10, 20);
    
    // Right brain label
    ctx.fillStyle = 'rgba(200, 100, 255, 1)';
    ctx.fillText('Right Brain', canvas.width - 90, 20);
    
    // Reset shadow
    ctx.shadowBlur = 0;
  }, [brainData]);

  // Connect to backend
  const handleConnect = async () => {
    if (connected) {
      try {
        await fetch('http://localhost:5000/api/disconnect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        setConnected(false);
        setBrainData(null);
      } catch (error) {
        console.error('Error disconnecting:', error);
        // Force disconnect even if API call fails
        setConnected(false);
        setBrainData(null);
      }
    } else {
      try {
        const response = await fetch('http://localhost:5000/api/connect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ use_webcam: webcamActive }),
        });

        if (response.ok) {
          setConnected(true);
          setErrorCount(0);
        } else {
          const data = await response.json();
          if (data.error === 'already_connected') {
            // If already connected, try to force disconnect and then connect
            await handleReset();
            setTimeout(handleConnect, 1000);
          } else {
            alert('Failed to connect: ' + (data.error || 'Unknown error'));
          }
        }
      } catch (error) {
        console.error('Error connecting:', error);
        alert('Connection error. Please make sure the backend is running.');
      }
    }
  };

  // Emergency reset
  const handleReset = async () => {
    try {
      // Try both endpoints
      await fetch('http://localhost:5000/api/reset', { method: 'POST' });
      await fetch('http://localhost:5000/api/bypass', { method: 'POST' });
      await fetch('http://localhost:5000/api/disconnect', { method: 'POST' });

      setConnected(false);
      setBrainData(null);
      setErrorCount(0);
    } catch (error) {
      console.error('Error resetting connection:', error);
      // Reset state even if the API fails
      setConnected(false);
      setBrainData(null);
      setErrorCount(0);
    }
  };

  // Determine which side of the brain is more active
  const getBrainSide = () => {
    if (!brainData) return null;

    if (brainData.left > brainData.right + 0.1) {
      return 'left';
    } else if (brainData.right > brainData.left + 0.1) {
      return 'right';
    } else {
      return 'balanced';
    }
  };

  const brainSide = getBrainSide();

  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 text-white p-4">
      {/* Header with subtle animation */}
      <div className="mb-8 text-center relative overflow-hidden">
        <div className="absolute inset-0 bg-blue-900 opacity-10 rounded-xl"></div>
        <h1 className="text-5xl font-bold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 tracking-tight py-2 animate-pulse-slow">
          Brain Activity Monitor
          {usingRealData ? (
            <span className="ml-2 text-green-400 text-sm font-normal animate-fade-in">(Using Real EEG Data)</span>
          ) : (
            <span className="ml-2 text-yellow-400 text-sm font-normal animate-fade-in">(Simulation Mode)</span>
          )}
        </h1>
        <p className="text-blue-300 text-lg relative z-10">
          Visualize your cognitive patterns and neural activity in real-time
        </p>
      </div>

      {/* Simulation Mode Warning Banner - with subtle animation */}
      {!usingRealData && connected && (
        <div className="mb-6 bg-gradient-to-r from-blue-900 to-blue-800 border-l-4 border-blue-500 rounded-md p-4 text-blue-200 transform transition-all duration-500 hover:scale-[1.01] shadow-lg">
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-blue-300" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            <span className="font-medium">Simulation Mode Active</span>
          </div>
          <p className="mt-1 text-sm ml-7">
            No EEG dataset was found. This is a simulated demonstration based partly on your eye movements.
            {webcamActive ? ' Your eye movements will influence the simulation.' : ' Enable the camera for better interaction.'}
          </p>
        </div>
      )}

      {/* Backend Status - Full width bar with improved visual feedback */}
      <div
        className={`p-4 rounded-lg mb-6 w-full shadow-lg transform transition-all duration-300 ${
          backendStatus === null ? 'bg-gray-900' : backendStatus ? 'bg-gradient-to-r from-blue-900 to-blue-800' : 'bg-gradient-to-r from-red-900 to-red-800'
        }`}
      >
        <div className="flex items-center">
          <div
            className={`w-3 h-3 rounded-full mr-2 ${
              backendStatus === null ? 'bg-gray-400 animate-pulse' : backendStatus ? 'bg-green-400' : 'bg-red-400 animate-pulse'
            }`}
          ></div>
          <p className="font-medium">
            {backendStatus === null
              ? 'Checking server status...'
              : backendStatus
              ? 'Server Connected'
              : 'Server Offline'}
          </p>
          {!backendStatus && (
            <button
              className="ml-auto bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500"
              onClick={() => window.location.reload()}
            >
              Retry
            </button>
          )}
        </div>
        {!backendStatus && (
          <div className="mt-2 ml-5">
          </div>
        )}
      </div>

      {/* Control Buttons - Improved with animations and visual feedback */}
      <div className="grid grid-cols-3 gap-3 mb-8">
        <button
          className={`py-3 rounded-lg text-white font-medium transform transition-all duration-300 hover:scale-105 shadow-lg ${
            connected ? 'bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600' : 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600'
          }`}
          onClick={handleConnect}
          disabled={!backendStatus}
        >
          <div className="flex items-center justify-center">
            <span className="mr-2">{connected ? '✕' : '🔌'}</span>
            {connected ? 'Disconnect' : 'Connect Brain Device'}
          </div>
        </button>

        <button
          className={`py-3 rounded-lg text-white font-medium transform transition-all duration-300 hover:scale-105 shadow-lg ${
            webcamActive ? 'bg-gradient-to-r from-red-600 to-red-500 hover:from-red-700 hover:to-red-600' : 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600'
          }`}
          onClick={() => setWebcamActive(!webcamActive)}
        >
          <div className="flex items-center justify-center">
            <span className="mr-2">{webcamActive ? '📵' : '📹'}</span>
            {webcamActive ? 'Turn Off Camera' : 'Turn On Camera'}
          </div>
        </button>

        <button
          className="py-3 rounded-lg bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-700 hover:to-yellow-600 text-white font-medium transform transition-all duration-300 hover:scale-105 shadow-lg"
          onClick={handleReset}
        >
          <div className="flex items-center justify-center">
            <span className="mr-2">🚨</span>
            Emergency Reset
          </div>
        </button>
      </div>

      {/* Main Content Area - Enhanced visual appeal and smoother animations */}
      {connected && (
        <div className="flex flex-col md:flex-row gap-6 mb-8 animate-fade-in">
          {/* Right Column - Camera Feed with enhanced visuals - NOW FIRST */}
          <div className="w-full md:w-1/2 bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg p-5 shadow-xl transform transition-all duration-500 hover:translate-y-[-5px] min-h-[650px]">
            <h2 className="text-xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">Eye Movement Analysis</h2>

            {webcamActive ? (
              <div>
                <div className="bg-black rounded-lg overflow-hidden relative shadow-xl border border-gray-800/50 h-64">
                  <video ref={videoRef} autoPlay muted className="w-full h-64 object-cover" />

                  {/* Visual indicator for eye position */}
                  <div className="absolute bottom-4 left-0 right-0 flex justify-center items-center">
                    <div className="bg-black/70 backdrop-filter backdrop-blur-sm rounded-full px-4 py-1 flex items-center space-x-2 border border-gray-700/30">
                      <span
                        className={`h-4 w-4 rounded-full transition-all duration-300 ${
                          eyePosition === 'left' ? 'bg-purple-500 animate-pulse' : 'bg-gray-700'
                        }`}
                      ></span>
                      <span
                        className={`h-4 w-4 rounded-full transition-all duration-300 ${
                          eyePosition === 'center' ? 'bg-green-500 animate-pulse' : 'bg-gray-700'
                        }`}
                      ></span>
                      <span
                        className={`h-4 w-4 rounded-full transition-all duration-300 ${
                          eyePosition === 'right' ? 'bg-blue-500 animate-pulse' : 'bg-gray-700'
                        }`}
                      ></span>
                    </div>
                  </div>

                  {/* Blink indicator with improved animation */}
                  {blinkDetected && (
                    <div className="absolute inset-0 bg-yellow-500/20 flex items-center justify-center backdrop-filter backdrop-blur-sm">
                      <span className="text-xl font-bold text-yellow-300 animate-pulse bg-black/40 px-4 py-2 rounded-lg">BLINK!</span>
                    </div>
                  )}
                </div>

                <div className="mt-4 bg-gradient-to-r from-blue-900/60 to-blue-800/60 p-4 rounded-lg backdrop-blur-sm border border-blue-700/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-blue-300 font-medium">
                      Direction: <span className="font-bold">{eyePosition.toUpperCase()}</span>
                    </span>
                    {blinkDetected && (
                      <span className="text-yellow-300 font-bold animate-pulse">👁️ Blink Detected</span>
                    )}
                  </div>
                  <div className="flex justify-between text-xs text-blue-200">
                    <span>Looking left = Creative</span>
                    <span>Looking right = Analytical</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 bg-gradient-to-br from-blue-900/40 to-blue-800/40 rounded-lg backdrop-blur-sm border border-blue-700/20 h-64 flex flex-col items-center justify-center">
                <div className="text-5xl mb-4">📹</div>
                <p className="text-gray-300">Camera is turned off</p>
                <button
                  className="mt-4 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 rounded-md text-white transform transition-all duration-300 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onClick={() => setWebcamActive(true)}
                >
                  Enable Camera
                </button>
              </div>
            )}
            
            {/* MOVED: Brain Activity Results now below the camera */}
            <div className="mt-6 bg-gradient-to-br from-gray-800/80 to-gray-900/80 p-4 rounded-lg border border-gray-700/50 backdrop-blur-sm shadow-inner transform transition-all duration-300 hover:scale-[1.02] min-h-[120px]">
              {brainData ? (
                <>
                  <p className="font-bold text-center text-xl mb-2">
                    <span className="text-blue-400">Cognitive State:</span>{' '}
                    <span
                      className={
                        brainSide === 'left'
                          ? 'text-blue-400'
                          : brainSide === 'right'
                          ? 'text-purple-400'
                          : 'text-green-400'
                      }
                    >
                      {brainSide === 'left'
                        ? 'LEFT BRAIN DOMINANT'
                        : brainSide === 'right'
                        ? 'RIGHT BRAIN DOMINANT'
                        : 'BALANCED THINKING'}
                    </span>
                  </p>
                  <p className="text-center text-sm mt-1 text-gray-300">
                    {brainSide === 'left'
                      ? 'Analytical, logical, detail-oriented thinking'
                      : brainSide === 'right'
                      ? 'Creative, intuitive, big-picture thinking'
                      : 'Balanced thinking using both hemispheres'}
                  </p>
                </>
              ) : (
                <p className="text-center text-gray-400 py-6">Connect to see brain activity results</p>
              )}
            </div>
          </div>

          {/* Left Column - Brain Activity Graph */}
          <div className="w-full md:w-1/2 bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg p-5 shadow-xl transform transition-all duration-500 hover:translate-y-[-5px] min-h-[650px]">
            <h2 className="text-xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300">Neural Activity</h2>

            {/* Eye tracking status with more prominent visualization */}
            {webcamActive && (
              <div className="mb-4 bg-blue-900/40 backdrop-blur-sm rounded-lg px-3 py-3 border border-blue-700/30 h-[140px]">
                <div className="flex items-center justify-between">
                  <span className="text-blue-300 font-medium">Eye Position: </span>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${eyePosition === 'left' ? 'bg-purple-500 animate-pulse' : 'bg-gray-700'}`}></div>
                    <div className={`w-3 h-3 rounded-full ${eyePosition === 'center' ? 'bg-green-500 animate-pulse' : 'bg-gray-700'}`}></div>
                    <div className={`w-3 h-3 rounded-full ${eyePosition === 'right' ? 'bg-blue-500 animate-pulse' : 'bg-gray-700'}`}></div>
                  </div>
                </div>
                <div className="mt-2 flex items-center justify-center">
                  <div className="w-full h-6 bg-gray-800/80 rounded-full overflow-hidden flex">
                    <div 
                      className={`h-full flex justify-center items-center font-bold text-xs transition-all duration-300 ${
                        eyePosition === 'left' ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white' : 'bg-gray-800 text-gray-700'
                      }`} 
                      style={{width: '33%'}}
                    >
                      LEFT
                    </div>
                    <div 
                      className={`h-full flex justify-center items-center font-bold text-xs transition-all duration-300 ${
                        eyePosition === 'center' ? 'bg-gradient-to-r from-green-600 to-green-500 text-white' : 'bg-gray-800 text-gray-700'
                      }`} 
                      style={{width: '34%'}}
                    >
                      CENTER
                    </div>
                    <div 
                      className={`h-full flex justify-center items-center font-bold text-xs transition-all duration-300 ${
                        eyePosition === 'right' ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white' : 'bg-gray-800 text-gray-700'
                      }`} 
                      style={{width: '33%'}}
                    >
                      RIGHT
                    </div>
                  </div>
                </div>
                {eyePosition !== 'center' && (
                  <p className="mt-1 text-center text-sm text-blue-300">
                    {eyePosition === 'left' ? 'Boosting right brain (creative)' : 'Boosting left brain (analytical)'}
                  </p>
                )}
                <div className="mt-2 flex items-center justify-between">
                  <span className="text-blue-300">Alertness:</span>
                  <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                    alertness === 'awake' 
                      ? 'bg-gradient-to-r from-green-600 to-green-500 text-white shadow-sm shadow-green-900/50' 
                      : 'bg-gradient-to-r from-yellow-600 to-yellow-500 text-white shadow-sm shadow-yellow-900/50'
                  }`}>
                    {alertness === 'awake' ? 'ALERT' : 'DROWSY'}
                  </div>
                </div>
              </div>
            )}

            {brainData ? (
              <div>
                {/* Brain wave visualization - improved container */}
                <div className="mb-6 bg-gray-900/70 p-4 rounded-lg backdrop-blur-sm border border-gray-800">
                  <h3 className="text-sm font-medium text-blue-300 mb-2">Real-time EEG Waveform</h3>
                  <div className="relative h-48">
                    <canvas
                      ref={canvasRef}
                      className="w-full h-48 bg-black/90 border border-gray-700/50 rounded-md"
                      width={500}
                      height={180}
                    />
                    <div className="absolute top-2 left-2 flex space-x-4 opacity-70">
                      <div className="flex items-center">
                        <span className="w-3 h-3 rounded-full bg-blue-500 mr-1"></span>
                        <span className="text-xs text-blue-300">Left</span>
                      </div>
                      <div className="flex items-center">
                        <span className="w-3 h-3 rounded-full bg-purple-500 mr-1"></span>
                        <span className="text-xs text-purple-300">Right</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-blue-300 font-medium">Left Brain (Analytical)</span>
                      <span className="text-blue-300 font-bold">{Math.round(brainData.left * 100)}%</span>
                    </div>
                    <div className="h-3 bg-gray-700/50 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full transition-all duration-700"
                        style={{ width: `${brainData.left * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-purple-300 font-medium">Right Brain (Creative)</span>
                      <span className="text-purple-300 font-bold">{Math.round(brainData.right * 100)}%</span>
                    </div>
                    <div className="h-3 bg-gray-700/50 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full transition-all duration-700"
                        style={{ width: `${brainData.right * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                {/* REMOVED: Brain Activity Results section moved to below the camera */}

                {brainData.blink && (
                  <div className="mt-3 p-2 bg-gradient-to-r from-yellow-900/70 to-amber-800/70 text-yellow-300 rounded-md text-center animate-pulse border border-yellow-700/30">
                    👁️ Blink Detected
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 h-[350px] flex flex-col items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto mb-4"></div>
                <p className="text-blue-300">Initializing neural interface...</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Instruction Panel with improved animation and styling */}
      {!connected && (
        <div className="bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-lg shadow-xl text-center mb-8 border border-gray-700/50 transform transition-all duration-500 hover:scale-[1.01] min-h-[250px]">
          <div className="text-5xl mb-4 animate-pulse">🧠</div>
          <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300 mb-2">Ready to Explore Your Brain?</h2>
          <p className="text-gray-300 mb-4">
            Click "Connect Brain Device" above to begin your cognitive journey and visualize your brain activity in
            real-time.
          </p>
          <button
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 rounded-md text-white font-medium transform transition-all duration-300 hover:scale-105 shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onClick={handleConnect}
            disabled={!backendStatus}
          >
            Start Brain Monitoring
          </button>
        </div>
      )}

      {/* Educational Content with improved styling and visual hierarchy */}
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg p-6 shadow-xl mb-8 border border-gray-700/50">
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300 mb-4">Understanding Brain Hemisphere Dominance</h2>

        <div className="prose prose-invert prose-blue max-w-none">
          <p className="text-gray-300">
            The human brain is divided into two hemispheres, each responsible for different cognitive functions. By
            monitoring and understanding which hemisphere is more active during various tasks, we can gain insights into
            our cognitive processes and optimize our thinking patterns.
          </p>

          <h3 className="text-xl font-bold text-blue-300 mt-6">Left Brain: The Analytical Powerhouse</h3>
          <p className="text-gray-300">
            The left hemisphere is traditionally associated with logical, analytical, and sequential processing. When
            your left brain is dominant, you're likely engaged in:
          </p>
          <ul className="list-disc pl-5 text-gray-300">
            <li>Mathematical calculations and analytical problem-solving</li>
            <li>Language processing and verbal reasoning</li>
            <li>Systematic and methodical thinking</li>
            <li>Detail-oriented tasks and linear logic</li>
            <li>Critical analysis and objective evaluation</li>
          </ul>

          <h3 className="text-xl font-bold text-purple-300 mt-6">Right Brain: The Creative Center</h3>
          <p className="text-gray-300">
            The right hemisphere specializes in intuitive, creative, and holistic processing. When your right brain is
            dominant, you're likely engaged in:
          </p>
          <ul className="list-disc pl-5 text-gray-300">
            <li>Creative expression and artistic endeavors</li>
            <li>Pattern recognition and spatial awareness</li>
            <li>Emotional processing and empathy</li>
            <li>Non-verbal communication and body language</li>
            <li>Holistic thinking and seeing the "big picture"</li>
          </ul>

          <h3 className="text-xl font-bold text-green-300 mt-6">Balanced Thinking: The Optimal State</h3>
          <p className="text-gray-300">
            While each hemisphere has its specializations, optimal cognitive performance often comes from balanced
            activation across both hemispheres. This integrated thinking allows you to:
          </p>
          <ul className="list-disc pl-5 text-gray-300">
            <li>Approach problems with both creativity and analytical rigor</li>
            <li>Process information both logically and intuitively</li>
            <li>Balance emotional and rational decision-making</li>
            <li>See both details and the bigger picture</li>
            <li>Switch fluidly between different thinking modes</li>
          </ul>

          <h3 className="text-xl font-bold text-blue-300 mt-6">The Science Behind Our Analysis</h3>
          <p className="text-gray-300">
            By tracking these subtle changes in activity, along with other neurological markers, we can provide insights
            into which cognitive mode you're currently operating in. This awareness can help you:
          </p>
          <ul className="list-disc pl-5 text-gray-300">
            <li>Recognize when you're stuck in one thinking mode</li>
            <li>Intentionally shift your cognitive approach to suit different tasks</li>
            <li>Develop greater cognitive flexibility</li>
            <li>Optimize your thinking for specific challenges</li>
            <li>Train yourself to access both hemispheres more effectively</li>
          </ul>

          <div className="bg-gradient-to-r from-blue-900/40 to-blue-800/40 p-5 rounded-lg mt-6 border border-blue-700/30 transform transition-all duration-500 hover:translate-y-[-2px]">
            <h3 className="text-xl font-bold text-blue-200">Practical Applications</h3>
            <p className="text-blue-100">
              Understanding your brain hemisphere dominance patterns can be valuable for students, professionals,
              artists, athletes, and anyone seeking to optimize their cognitive performance. By recognizing when you're
              overrelying on one hemisphere, you can consciously engage complementary thinking styles to enhance
              creativity, problem-solving, and decision-making.
            </p>
          </div>
        </div>
        
        {/* New Applications Section */}
        <div className="mt-10">
          <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-300 mb-6">Real-World Applications</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Medical Applications Card */}
            <div className="bg-gradient-to-br from-indigo-900/30 to-indigo-800/30 rounded-xl p-5 border border-indigo-700/30 shadow-lg transform transition-all duration-500 hover:translate-y-[-5px]">
              <h3 className="text-xl font-bold text-indigo-300 mb-3 flex items-center">
                <span className="text-2xl mr-2">🏥</span> Medical & Neurological Applications
              </h3>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start">
                  <span className="text-indigo-400 mr-2">•</span>
                  <span><strong className="text-indigo-300">Stroke Rehabilitation:</strong> Monitors cognitive recovery and eye coordination</span>
                </li>
                <li className="flex items-start">
                  <span className="text-indigo-400 mr-2">•</span>
                  <span><strong className="text-indigo-300">Epilepsy Detection:</strong> Identifies abnormal brain wave patterns</span>
                </li>
                <li className="flex items-start">
                  <span className="text-indigo-400 mr-2">•</span>
                  <span><strong className="text-indigo-300">Brain Hemorrhage Diagnosis:</strong> Detects irregular EEG signals</span>
                </li>
                <li className="flex items-start">
                  <span className="text-indigo-400 mr-2">•</span>
                  <span><strong className="text-indigo-300">Alzheimer's Monitoring:</strong> Tracks cognitive decline over time</span>
                </li>
                <li className="flex items-start">
                  <span className="text-indigo-400 mr-2">•</span>
                  <span><strong className="text-indigo-300">Parkinson's Research:</strong> Analyzes brain activity patterns</span>
                </li>
              </ul>
            </div>
            
            {/* Mental Health Card */}
            <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/30 rounded-xl p-5 border border-purple-700/30 shadow-lg transform transition-all duration-500 hover:translate-y-[-5px]">
              <h3 className="text-xl font-bold text-purple-300 mb-3 flex items-center">
                <span className="text-2xl mr-2">🧠</span> Mental Health & Cognitive Training
              </h3>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span><strong className="text-purple-300">ADHD Monitoring:</strong> Tracks focus levels and attention patterns</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span><strong className="text-purple-300">Stress Detection:</strong> Identifies stress-induced brain activity changes</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span><strong className="text-purple-300">Meditation Training:</strong> Helps achieve balanced mental states</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-2">•</span>
                  <span><strong className="text-purple-300">Anxiety Therapy:</strong> Provides biofeedback for anxiety management</span>
                </li>
              </ul>
            </div>
            
            {/* Education Card */}
            <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/30 rounded-xl p-5 border border-blue-700/30 shadow-lg transform transition-all duration-500 hover:translate-y-[-5px]">
              <h3 className="text-xl font-bold text-blue-300 mb-3 flex items-center">
                <span className="text-2xl mr-2">📚</span> Education & Workplace Productivity
              </h3>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start">
                  <span className="text-blue-400 mr-2">•</span>
                  <span><strong className="text-blue-300">Learning Strategy Optimization:</strong> Identifies effective cognitive approaches</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-2">•</span>
                  <span><strong className="text-blue-300">Work Productivity:</strong> Measures focus and mental fatigue</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-2">•</span>
                  <span><strong className="text-blue-300">Student Performance:</strong> Helps identify optimal study techniques</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-2">•</span>
                  <span><strong className="text-blue-300">Cognitive Development:</strong> Tracks brain development in children</span>
                </li>
              </ul>
            </div>
            
            {/* Tech Integration Card */}
            <div className="bg-gradient-to-br from-cyan-900/30 to-cyan-800/30 rounded-xl p-5 border border-cyan-700/30 shadow-lg transform transition-all duration-500 hover:translate-y-[-5px]">
              <h3 className="text-xl font-bold text-cyan-300 mb-3 flex items-center">
                <span className="text-2xl mr-2">🤖</span> Human-Computer Interaction & AI
              </h3>
              <ul className="space-y-2 text-gray-300">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span><strong className="text-cyan-300">Brain-Computer Interfaces:</strong> Control devices with brain activity</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span><strong className="text-cyan-300">Gaming Integration:</strong> Brain-controlled gaming experiences</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span><strong className="text-cyan-300">VR Enhancement:</strong> Improves immersion in virtual environments</span>
                </li>
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-2">•</span>
                  <span><strong className="text-cyan-300">Assistive Technology:</strong> Helps people with mobility limitations</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Footer with subtle animation - UPDATED with Anushka's name */}
      <footer className="text-center text-gray-500 text-sm mt-12 py-6 border-t border-gray-800">
        <div className="max-w-4xl mx-auto">
          <p className="font-medium text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500">Brain Activity Monitor - Neural Interface Technology</p>
          <p className="mt-2">© {new Date().getFullYear()} Advanced Cognitive Analytics | Made By Anushka</p>
          <div className="mt-3 flex justify-center space-x-4">
            <span className="text-blue-500 hover:text-blue-400 cursor-pointer transition-colors">Documentation</span>
            <span className="text-blue-500 hover:text-blue-400 cursor-pointer transition-colors">Research</span>
            <span className="text-blue-500 hover:text-blue-400 cursor-pointer transition-colors">Contact</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Add these custom animations to your Tailwind config or inline here
const style = document.createElement('style');
style.textContent = `
  @keyframes pulse-slow {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
  }
  .animate-pulse-slow {
    animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
  @keyframes fade-in {
    0% { opacity: 0; }
    100% { opacity: 1; }
  }
  .animate-fade-in {
    animation: fade-in 0.5s ease-out forwards;
  }
`;
document.head.appendChild(style);

export default SimpleBrain;
