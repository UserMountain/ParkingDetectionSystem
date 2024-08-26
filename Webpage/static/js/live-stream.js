document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.floating-nav a');
    const endStreamButton = document.getElementById('end-stream');
    const startStreamButton = document.getElementById('start-stream');
    const video = document.getElementById('live-video');
    const noStreamIcon = document.getElementById('no-stream-icon');
    const liveIcon = document.getElementById('live-icon');

  // Initialize the icons' visibility
    noStreamIcon.classList.remove('hidden');
    liveIcon.classList.add('hidden');

    // Toggle navigation menu
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }

    // Navigate to different pages
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent the default anchor behavior
            const targetPage = link.getAttribute('href'); // Get the href attribute
            window.location.href = targetPage; // Redirect to the target page
        });
    });

    // Drone connection and video stream
    const connectDroneButton = document.getElementById('connect-drone');
    const droneStatus = document.getElementById('drone-status');

    // Connect to drone and start video feed
    function connectDrone() {
        connectDroneButton.disabled = true; // Disable button to prevent multiple clicks

        fetch('/connect_drone', { method: 'POST' })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok.');
                return response.json();
            })
            .then(data => {
                if (data.status === 'Drone connected') {
                    updateDroneStatus('Connected', data.video_feed_status);
                    video.src = '/video_feed'; // Start video feed after successful connection
                } else {
                    throw new Error('Failed to connect to drone.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to connect to drone. Please try again.');
                updateDroneStatus('Not Connected');
            })
            .finally(() => {
                connectDroneButton.disabled = false; // Re-enable button
            });
    }

    function updateDroneStatus(connectionStatus, videoFeedStatus = '') {
        droneStatus.innerHTML = `Drone Connection Status: ${connectionStatus}`;
        if (videoFeedStatus) {
            droneStatus.innerHTML += `<br>Video Feed Status: ${videoFeedStatus}`;
        }
    }

    if (connectDroneButton) {
        connectDroneButton.addEventListener('click', connectDrone);
    }

    // Periodically check drone status
    function checkDroneStatus() {
        fetch('/drone_status')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok.');
                return response.json();
            })
            .then(data => {
                const connectionStatus = data.connected ? 'Connected' : 'Not Connected';
                updateDroneStatus(connectionStatus, data.video_feed_status);
            })
            .catch(error => {
                console.error('Error checking drone status:', error);
                updateDroneStatus('Unable to check');
            });
    }

    // Start the video stream
    if (startStreamButton) {
        startStreamButton.addEventListener('click', () => {
            fetch('/start_stream', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        video.src = '/video_feed';
                        noStreamIcon.classList.add('hidden');
                        liveIcon.classList.remove('hidden');
                    } else {
                        alert('Failed to start video stream: ' + data.error);
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    }

    // End the video stream
    if (endStreamButton) {
        endStreamButton.addEventListener('click', () => {
            fetch('/end_stream', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        video.src = '';
                        noStreamIcon.classList.remove('hidden');
                        liveIcon.classList.add('hidden');
                    } else {
                        console.error('Failed to end stream');
                    }
                })
                .catch(error => {
                    console.error('Error ending video stream:', error);
                });
        });
    }

    setInterval(checkDroneStatus, 5000); // Check every 5 seconds
});
