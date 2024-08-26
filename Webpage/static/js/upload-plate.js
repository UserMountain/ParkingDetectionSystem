document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.getElementById('image-input');
    const previewImage = document.getElementById('preview-image');
    const licenseText = document.getElementById('license-text');
    const editLicenseText = document.getElementById('edit-license-text');
    const editButton = document.getElementById('edit-button');
    const saveButton = document.getElementById('save-button');
    const totalImagesDisplay = document.getElementById('total-images');
    let images = [];
    let currentIndex = 0;

    function updateImageDisplay() {
        if (images.length > 0 && images[currentIndex]) {
            const currentImage = images[currentIndex];
            previewImage.src = currentImage.url;
            previewImage.alt = 'Processed Image';
            previewImage.style.display = 'block';
            licenseText.textContent = currentImage.licensePlate || 'N/A';
            totalImagesDisplay.textContent = `Total Images: ${images.length}`;
        } else {
            previewImage.style.display = 'none';
            licenseText.textContent = 'N/A';
            totalImagesDisplay.textContent = 'Total Images: 0';
        }
    }

    document.getElementById('upload-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const file = imageInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('image_name', file);

            fetch('/page2', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Error: ${data.error}`);
                } else {
                    images.push({
                        id: data.data_id,
                        url: data.image_url,
                        licensePlate: data.license_plate_number
                    });
                    currentIndex = images.length - 1;
                    updateImageDisplay();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to process image. Please try again.');
            });
        }
    });

    editButton.addEventListener('click', () => {
        editLicenseText.value = licenseText.textContent;
        editLicenseText.style.display = 'inline-block';
        licenseText.style.display = 'none';
        editButton.style.display = 'none';
        saveButton.style.display = 'inline-block';
    });

    saveButton.addEventListener('click', () => {
        const newText = editLicenseText.value;
        const imageId = images[currentIndex].id;
        fetch(`/update_text/${imageId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ new_text: newText })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Text updated successfully');
                images[currentIndex].licensePlate = newText;
                licenseText.textContent = newText;
            } else {
                alert(`Failed to update text: ${data.error}`);
            }
            editLicenseText.style.display = 'none';
            licenseText.style.display = 'block';
            editButton.style.display = 'inline-block';
            saveButton.style.display = 'none';
        })
        .catch(error => {
            console.error('Error updating text:', error);
            alert('Failed to update text.');
        });
    });

    document.getElementById('next-button').addEventListener('click', () => {
        if (currentIndex < images.length - 1) {
            currentIndex++;
            updateImageDisplay();
        }
    });

    document.getElementById('prev-button').addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateImageDisplay();
        }
    });

    document.getElementById('delete-button').addEventListener('click', () => {
        if (images.length > 0 && confirm('Are you sure you want to delete this image?')) {
            const imageId = images[currentIndex].id;
            fetch(`/delete_image/${imageId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    images.splice(currentIndex, 1);
                    currentIndex = Math.max(currentIndex - 1, 0);
                    updateImageDisplay();
                    alert('Image deleted successfully.');
                } else {
                    alert('Failed to delete image.');
                }
            })
            .catch(error => {
                console.error('Error deleting image:', error);
                alert('Failed to delete image.');
            });
        }
    });

    function fetchTotalImages() {
        fetch('/total-images')
            .then(response => response.json())
            .then(data => {
                totalImagesDisplay.textContent = `Total Images: ${data.total}`;
            })
            .catch(error => {
                console.error('Error fetching total images:', error);
            });
    }

    fetchTotalImages(); // Initial call to set the total images count
});
