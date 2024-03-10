const container = document.getElementById('container');
const timeline = document.getElementById('timeline-images');
const durationSelect = document.getElementById('duration-select');
const transitionSelect = document.getElementById('transition-select');
let selectedImages = [];

// Function to handle image selection
function toggleImageSelection(event) {
    const image = event.target;
    image.classList.toggle('selected');
    if (image.classList.contains('selected')) {
    selectedImages.push({ src: image.src, duration: parseInt(durationSelect.value), transition: transitionSelect.value });
    } else {
    selectedImages = selectedImages.filter(selectedImage => selectedImage.src !== image.src);
    }
    updateTimeline();
}

// Function to update the timeline with selected images
function updateTimeline() {
timeline.innerHTML = '';
if (selectedImages && selectedImages.length > 0) { // Check if selectedImages is defined and not empty
    selectedImages.forEach(selectedImage => {
    if (selectedImage && selectedImage.src && selectedImage.duration) { // Check if selectedImage is defined and has necessary properties
        const imageContainer = document.createElement('div');
        imageContainer.classList.add('timeline-image', 'bg-gray-700', 'rounded-md', 'p-2');
        imageContainer.style.width = '${selectedImage.duration * 20}px'; // Adjust scale factor as needed
        const imageElement = document.createElement('img');
        imageElement.src = selectedImage.src;
        imageElement.classList.add('w-full', 'h-auto');
        imageContainer.appendChild(imageElement);
        timeline.appendChild(imageContainer);
    }
    });
}
}

// Attach event listeners to images in the container
const images = document.querySelectorAll('.image');
images.forEach(image => {
    image.addEventListener('click', toggleImageSelection);
});

// Drag and Drop functionality for reordering images on the timeline
// Drag and Drop functionality for reordering images on the timeline
timeline.addEventListener('dragstart', (event) => {
const index = Array.from(event.target.parentNode.children).indexOf(event.target);
event.dataTransfer.setData('text/plain', index);
});

timeline.addEventListener('dragover', (event) => {
event.preventDefault(); // Prevent default behavior
});

timeline.addEventListener('drop', (event) => {
event.preventDefault(); // Prevent default behavior
const index = event.dataTransfer.getData('text/plain');
const draggedImage = selectedImages[index];
selectedImages.splice(index, 1); // Remove dragged image from its original position
const dropIndex = getIndex(event.clientX, timeline);
selectedImages.splice(dropIndex, 0, draggedImage); // Insert dragged image at drop position
updateTimeline();
});


// Function to get the index of drop position
function getIndex(x, timeline) {
    const images = document.querySelectorAll('.timeline-image');
    for (let i = 0; i < images.length; i++) {
    const rect = images[i].getBoundingClientRect();
    if (x < rect.left + rect.width / 2) {
        return i;
    }
    }
    return images.length;
}