document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');

    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    function fetchAndDisplayData() {
        const vehicleTable = document.querySelector('#vehicle-table tbody');
        vehicleTable.innerHTML = ''; // Clear the table before adding new data to avoid duplication

        fetch('/api/get_image_data')
            .then(response => response.json())
            .then(data => {
                let displayId = 1; // Start display ID at 1
                data.forEach(entry => {
                    addEntryToTable(entry, displayId++);
                });
                updateDeleteButtonListeners(); // Update listeners after data is fetched and table is populated
            })
            .catch(error => console.error('Error fetching vehicle data:', error));
    }

    function addEntryToTable(entry, displayId) {
        const vehicleTable = document.querySelector('#vehicle-table tbody');
        const row = document.createElement('tr');
        row.id = `data-row-${entry.id}`;
        row.innerHTML = `
            <td>${displayId}</td>  <!-- Use displayId instead of entry.id for visual representation -->
            <td><img src="/static/${entry.image_path}" alt="Vehicle Image" style="width: 100px;"></td>
            <td>${entry.text_data}</td>
            <td>
                <button class="delete-button" data-id="${entry.id}">Delete</button>
            </td>
        `;
        vehicleTable.appendChild(row);
    }

    function updateDeleteButtonListeners() {
        const deleteButtons = document.querySelectorAll('.delete-button');
        deleteButtons.forEach(button => {
            button.removeEventListener('click', handleDelete); // Remove existing event listeners to avoid multiple bindings
            button.addEventListener('click', handleDelete);
        });
    }

    function handleDelete(event) {
        const dataId = this.getAttribute('data-id');
        if (confirm('Are you sure you want to delete this record?')) {
            fetch(`/delete_image/${dataId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const row = document.getElementById(`data-row-${dataId}`);
                        if (row) {
                            row.remove();
                            fetchAndDisplayData(); // Refresh display to update IDs
                        }
                    } else {
                        alert(data.message); // Use the server's response message
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting record.');
                });
        }
    }

    fetchAndDisplayData(); // Initial fetch when page loads
});
