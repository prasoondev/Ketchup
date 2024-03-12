const container = document.getElementById('container');
const timeline = document.getElementById('timeline-images');
const upload_msg = document.getElementById('header-container');
const durationSelect = document.getElementById('duration-select');
const transitionSelect = document.getElementById('transition-select');
let selectedImages = [];

// Load selected images from Local Storage if available
window.addEventListener('DOMContentLoaded', function() {
    const savedImages = localStorage.getItem('selectedImages');
    if (savedImages) {
        selectedImages = JSON.parse(savedImages);
        updateTimeline();
    }
});

// Function to handle image selection
function toggleImageSelection(event) {
    const image = event.target;
    const imageSrc = image.src;
    const foundImageIndex = selectedImages.findIndex(img => img.src === imageSrc);

    if (image.classList.contains('selected')) {
        image.classList.remove('selected');
        if (foundImageIndex !== -1) {
            selectedImages.splice(foundImageIndex, 1);
        }
    } else {
        image.classList.add('selected');
        if (foundImageIndex === -1) {
            selectedImages.push({ src: imageSrc, selected: true, duration: parseInt(durationSelect.value), transition: transitionSelect.value });
        }
    }
    updateTimeline();
    saveSelectedImagesToStorage();
}

// Function to update the timeline with selected images
function updateTimeline() {
    timeline.innerHTML = '';
    if (selectedImages && selectedImages.length > 0) {
        selectedImages.forEach(selectedImage => {
            if (selectedImage && selectedImage.src && selectedImage.duration) {
                const imageContainer = document.createElement('div');
                imageContainer.classList.add('timeline-image', 'bg-red-500', 'rounded-xl', 'p-2');
                imageContainer.style.width = `${selectedImage.duration * 20}px`;

                const imageElement = document.createElement('img');
                imageElement.src = selectedImage.src;
                imageElement.classList.add('w-full', 'h-auto');

                if (selectedImage.selected) {
                    imageElement.classList.add('selected');
                }

                imageContainer.appendChild(imageElement);
                timeline.appendChild(imageContainer);
            }
        });
    }
}

function loadSelectedStateFromStorage() {
    selectedImages.forEach(selectedImage => {
        const imageElement = document.querySelector(`img[src="${selectedImage.src}"]`);
        if (imageElement) {
            if (selectedImage.selected) {
                imageElement.classList.add('selected');
            } else {
                imageElement.classList.remove('selected');
            }
        }
    });
}

// Attach event listeners to images in the container
const images = document.querySelectorAll('.image');
images.forEach(image => {
    image.addEventListener('click', toggleImageSelection);
});

// Add event listener to the "Create a Video" button
document.addEventListener('DOMContentLoaded', function() {
    // Get a reference to the "Create a Video" button
    const createVideoButton = document.querySelector('.create-video-button');

    // Add an event listener to the "Create a Video" button
    createVideoButton.addEventListener('click', function() {
        // Call the function to send selected images data to Python backend
        sendSelectedImagesToPython();
    });
});

// Function to save selected images to Local Storage
function saveSelectedImagesToStorage() {
    localStorage.setItem('selectedImages', JSON.stringify(selectedImages));
}

// Function to send selected images data to Python backend
function sendSelectedImagesToPython() {
    // Make sure there are selected images to send
    if (selectedImages.length > 0) {
        // Create a new XMLHttpRequest object
        const xhr = new XMLHttpRequest();
        
        // Define the URL of your Python backend endpoint
        const url = 'http://127.0.0.1:5000/receive-images';
        
        // Define the data to send to the backend (convert to JSON format)
        const data = JSON.stringify({ images: selectedImages });
        
        // Open a POST request to the backend URL
        xhr.open('POST', url, true);
        
        // Set the Content-Type header to JSON
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        // Define a callback function to handle the response from the backend
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    // Request was successful
                    console.log('Selected images data sent successfully to Python backend.');
                } else {
                    // Request failed
                    console.error('Failed to send selected images data to Python backend.');
                }
            }
        };
        
        // Send the data to the backend
        xhr.send(data);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Get a reference to the "Create a Video" button
    const createVideoButton = document.querySelector('.create-video-button');

    // Add an event listener to the "Create a Video" button
    createVideoButton.addEventListener('click', function() {
        // Call the function to send selected images data to Python backend
        sendSelectedImagesToPython();

        // Add text to the timeline container
        const uploadText = document.createElement('p');
        uploadText.textContent = 'Uploaded Successfully';
        uploadText.classList.add('text-red-500', 'text-center', 'font-bold');
        upload_msg.appendChild(uploadText);

        // Remove the text after 3 seconds
        setTimeout(function() {
            upload_msg.removeChild(uploadText);
        }, 3000);
    });
});

// Function to clear the selection
function clearSelection() {
    // Clear selected images array
    selectedImages = [];
    // Clear Local Storage
    localStorage.removeItem('selectedImages');
    // Deselect any selected images in the gallery
    const selectedImageElements = document.querySelectorAll('.image.selected');
    selectedImageElements.forEach(image => {
        image.classList.remove('selected');
    });
    // Update the timeline
    updateTimeline();
}

document.addEventListener('DOMContentLoaded', function() {
    // Get a reference to the "Clear Selection" button
    const clearSelectionButton = document.getElementById('clear-selection');

    // Add an event listener to the "Clear Selection" button
    clearSelectionButton.addEventListener('click', function() {
        // Call the function to clear the selection
        clearSelection();
    });
});

