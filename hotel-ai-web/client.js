// Hotel Messaria WebRTC Client
// Connects to Pipecat SmallWebRTC runner

const config = {
    baseUrl: 'https://c2da5032f055.ngrok-free.app', // Ngrok tunnel to local bot
    endpoints: {
        offer: '/api/offer',
    }
};

const state = {
    pc: null,
    isConnecting: false,
    isConnected: false,
    sessionId: null
};

// DOM Elements
const callBtn = document.getElementById('call-btn');
const statusContainer = document.getElementById('status-container');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');
const visualizer = document.getElementById('visualizer');
const instructionText = document.getElementById('instruction-text');
const remoteAudio = document.getElementById('remote-audio');

// Event Listeners
callBtn.addEventListener('click', toggleCall);

async function toggleCall() {
    if (state.isConnected || state.isConnecting) {
        endCall();
    } else {
        startCall();
    }
}

async function startCall() {
    console.log('🎯 [START] Initiating call...');
    console.log('📡 [CONFIG] Base URL:', config.baseUrl);
    updateStatus('connecting', 'Connecting to reception...');
    state.isConnecting = true;

    try {
        // 1. Create PeerConnection
        console.log('🔧 [STEP 1] Creating PeerConnection...');
        state.pc = new RTCPeerConnection({
            iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
        });
        console.log('✅ [STEP 1] PeerConnection created');

        // Monitor connection state
        state.pc.onconnectionstatechange = () => {
            console.log('🔌 [STATE] Connection state:', state.pc.connectionState);
        };

        state.pc.oniceconnectionstatechange = () => {
            console.log('❄️ [STATE] ICE connection state:', state.pc.iceConnectionState);
        };

        state.pc.onicegatheringstatechange = () => {
            console.log('📥 [STATE] ICE gathering state:', state.pc.iceGatheringState);
        };

        // 2. Handle Remote Audio
        state.pc.ontrack = (event) => {
            console.log('🎵 [TRACK] Received remote track:', event.track.kind, event.track);
            console.log('🎵 [TRACK] Streams:', event.streams);
            if (event.track.kind === 'audio') {
                remoteAudio.srcObject = event.streams[0];
                console.log('✅ [AUDIO] Remote audio connected to element');

                // Don't show connected immediately. Wait for audio energy.
                updateStatus('waiting', 'Waiting for agent...');

                // Initialize Audio Context for detection
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioCtx.createMediaStreamSource(event.streams[0]);
                const analyser = audioCtx.createAnalyser();
                analyser.fftSize = 256;
                source.connect(analyser);

                const bufferLength = analyser.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);

                // Check for audio energy
                const checkAudio = () => {
                    if (!state.isConnecting && !state.isConnected) return; // Stop if call ended

                    analyser.getByteFrequencyData(dataArray);
                    let sum = 0;
                    for (let i = 0; i < bufferLength; i++) {
                        sum += dataArray[i];
                    }
                    const average = sum / bufferLength;

                    // Threshold for speech detection (adjust if needed)
                    if (average > 10 && !state.hasSpoken) {
                        console.log('🗣️ [AUDIO] Speech detected! Avg energy:', average);
                        state.hasSpoken = true;
                        updateStatus('connected', 'Connected');
                        showVisualizer(true);
                    }

                    if (!state.hasSpoken) {
                        requestAnimationFrame(checkAudio);
                    }
                };

                state.hasSpoken = false;
                checkAudio();
            }
        };

        // 3. Handle ICE Candidates
        state.pc.onicecandidate = (event) => {
            if (event.candidate) {
                console.log('❄️ [ICE] New candidate:', event.candidate.candidate.substring(0, 50) + '...');
                sendCandidate(event.candidate);
            } else {
                console.log('❄️ [ICE] All candidates gathered');
            }
        };

        // 4. Add Transceiver (Audio only)
        console.log('🔧 [STEP 2] Adding audio transceiver...');
        state.pc.addTransceiver('audio', { direction: 'sendrecv' });
        console.log('✅ [STEP 2] Audio transceiver added');

        // 5. Create Offer
        console.log('🔧 [STEP 3] Creating offer...');
        const offer = await state.pc.createOffer();
        console.log('✅ [STEP 3] Offer created:', offer.type);
        console.log('📄 [SDP] Offer SDP (first 100 chars):', offer.sdp.substring(0, 100) + '...');

        await state.pc.setLocalDescription(offer);
        console.log('✅ [STEP 3] Local description set');

        // 6. Send Offer to Server
        console.log('🔧 [STEP 4] Sending offer to server...');
        console.log('📡 [HTTP] POST', `${config.baseUrl}${config.endpoints.offer}`);

        const response = await fetch(`${config.baseUrl}${config.endpoints.offer}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type
            })
        });

        console.log('📡 [HTTP] Response status:', response.status, response.statusText);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ [HTTP] Error response:', errorText);
            throw new Error(`Server error: ${response.status}`);
        }

        const answer = await response.json();
        console.log('✅ [STEP 4] Received answer:', answer.type);
        console.log('📄 [SDP] Answer SDP (first 100 chars):', answer.sdp ? answer.sdp.substring(0, 100) + '...' : 'N/A');

        // 7. Set Remote Description
        console.log('🔧 [STEP 5] Setting remote description...');
        await state.pc.setRemoteDescription(answer);
        console.log('✅ [STEP 5] Remote description set');

        // Update UI
        state.isConnected = true;
        state.isConnecting = false;
        console.log('🎉 [SUCCESS] Call established!');

        callBtn.classList.add('bg-red-500');
        callBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
        `;
        instructionText.textContent = "Tap to end call";

    } catch (error) {
        console.error('❌ [ERROR] Connection failed:', error);
        console.error('❌ [ERROR] Stack:', error.stack);
        updateStatus('error', 'Connection failed. Try again.');
        endCall();
    }
}

async function sendCandidate(candidate) {
    try {
        console.log('📤 [ICE] Sending candidate to server...');
        const response = await fetch(`${config.baseUrl}${config.endpoints.offer}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                candidates: [{
                    candidate: candidate.candidate,
                    sdp_mid: candidate.sdpMid,
                    sdp_mline_index: candidate.sdpMLineIndex
                }]
            })
        });
        console.log('✅ [ICE] Candidate sent, response:', response.status);
    } catch (e) {
        console.error('❌ [ICE] Failed to send candidate:', e);
    }
}

function endCall() {
    console.log('🔴 [END] Ending call...');
    if (state.pc) {
        console.log('🔌 [END] Closing PeerConnection, state:', state.pc.connectionState);
        state.pc.close();
        state.pc = null;
    }
    state.isConnected = false;
    state.isConnecting = false;
    state.hasSpoken = false;
    console.log('✅ [END] Call ended');

    // Reset UI
    updateStatus('ready', 'Call ended');
    setTimeout(() => {
        statusContainer.classList.remove('opacity-100');
        statusContainer.classList.add('opacity-0');
    }, 2000);

    showVisualizer(false);
    callBtn.classList.remove('bg-red-500');
    callBtn.classList.add('bg-white');
    callBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-brand-900 transition-colors group-hover:text-brand-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
    `;
    instructionText.textContent = "Tap to speak with reception";
}

// DOM Elements
const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('progress-bar');

function updateStatus(type, message) {
    statusContainer.classList.remove('opacity-0', 'translate-y-4');
    statusContainer.classList.add('opacity-100', 'translate-y-0');

    // Smooth text transition
    if (statusText.textContent !== message) {
        statusText.classList.add('opacity-0');
        setTimeout(() => {
            statusText.textContent = message;
            statusText.classList.remove('opacity-0');
        }, 300);
    }

    statusDot.className = 'w-2 h-2 rounded-full transition-colors duration-500';

    // Reset progress bar classes
    progressBar.className = 'h-full bg-brand-500 transition-all duration-300 ease-out';

    if (type === 'connecting') {
        statusDot.classList.add('bg-yellow-400', 'animate-pulse');
        // Show progress bar
        progressContainer.classList.remove('opacity-0');
        progressBar.style.width = '60%'; // Simulate initial connection progress
        progressBar.classList.add('animate-pulse');
    }
    else if (type === 'waiting') { // New state for "Waiting for agent..."
        statusDot.classList.add('bg-yellow-400', 'animate-pulse');
        progressContainer.classList.remove('opacity-0');
        progressBar.style.width = '90%'; // Almost there
        progressBar.classList.add('animate-pulse');
    }
    else if (type === 'connected') {
        statusDot.classList.add('bg-green-500', 'shadow-[0_0_10px_#22c55e]');
        // Complete and hide progress bar
        progressBar.style.width = '100%';
        setTimeout(() => {
            progressContainer.classList.add('opacity-0');
            setTimeout(() => { progressBar.style.width = '0%'; }, 300);
        }, 500);
    }
    else if (type === 'error') {
        statusDot.classList.add('bg-red-500');
        progressContainer.classList.add('opacity-0');
        progressBar.style.width = '0%';
    }
    else {
        statusDot.classList.add('bg-gray-400');
        progressContainer.classList.add('opacity-0');
        progressBar.style.width = '0%';
    }
}

function showVisualizer(show) {
    if (show) {
        visualizer.classList.remove('hidden');
    } else {
        visualizer.classList.add('hidden');
    }
}
