document.addEventListener('keydown', function(event) {
    let command = null;

    switch(event.code) {
        case 'ArrowLeft':
            command = 'left';
            break;
        case 'ArrowRight':
            command = 'right';
            break;
        case 'ArrowUp':
            command = 'forward';
            break;
        case 'ArrowDown':
            command = 'backward';
            break;
        case 'KeyW':
            command = 'up';
            break;
        case 'KeyS':
            command = 'down';
            break;
        case 'KeyA':
            command = 'rotate_left';
            break;
        case 'KeyD':
            command = 'rotate_right';
            break;
        case 'KeyQ':
            command = 'land';
            break;
        case 'KeyE':
            command = 'takeoff';
            break;
        case 'Enter':
            fetch('/capture_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ capture: true })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Image captured:', data.filename);
                } else {
                    console.error('Error capturing image:', data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
            return; // Skip the fetch call for drone control commands
    }

    if (command) {
        fetch('/control_drone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Drone command executed:', command);
            } else {
                console.error('Error executing drone command:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});
