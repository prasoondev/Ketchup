const container = document.getElementById('container');
const timeline = document.getElementById('timeline-images');
const timelineAudios = document.getElementById('timeline-audios');
const upload_msg = document.getElementById('header-container');
const durationSelect = document.getElementById('duration-select');
const transitionSelect = document.getElementById('transition-select');
const audioSelect = document.getElementById('audio-select');
const resolutionSelect = document.getElementById('resolution-select');
let selectedImages = [];
let selectedAudios = [];

// Load selected images from Local Storage if available
// This part is removed

// Load selected audios from Local Storage if available
// This part is removed

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
}

function toggleAudioSelection(audio) {
    const audioSrc = audio.querySelector('audio source').src; // Get the source of the audio
    const audioLabel = audio.querySelector('label').textContent;
    const audioName = audioLabel.replace('.mp3', '');
    const foundAudioIndex = selectedAudios.findIndex(aud => aud.src === audioSrc);

    if (audio.classList.contains('selected')) {
        audio.classList.remove('selected');
        if (foundAudioIndex !== -1) {
            selectedAudios.splice(foundAudioIndex, 1);
        }
    } else {
        audio.classList.add('selected');
        if (foundAudioIndex === -1) {
            selectedAudios.push({ src: audioSrc, selected: true, duration: parseInt(durationSelect.value), name: audioName });
        }
    }
    updateAudioTimeline(); // Update the audio timeline after selecting/deselecting audio
}

// Function to update the timeline with selected images
function updateTimeline() {
    timeline.innerHTML = '';
    if (selectedImages && selectedImages.length > 0) {
        selectedImages.forEach(selectedImage => {
            if (selectedImage && selectedImage.src && selectedImage.duration) {
                const formContainer = document.createElement('div');
                formContainer.classList.add('timeline-image', 'rounded-xl', 'p-2');
                formContainer.style.minWidth = '100px'; // Set the minimum width here
                formContainer.style.width = `${selectedImage.duration * 100}px`;

                const formElement = document.createElement('form');
                formElement.style.backgroundImage = `url('${selectedImage.src}')`;
                formElement.style.backgroundSize = 'cover';
                formElement.style.backgroundPosition = 'center';
                formElement.style.padding = '10px';
                formElement.style.borderRadius = '5px';
                formElement.style.textAlign = 'center';
                formElement.style.alignItems = 'center';
                formElement.style.minWidth = '40px';

                const durationInput = document.createElement('input');
                durationInput.type = 'number';
                durationInput.min = 1;
                durationInput.value = selectedImage.duration;
                durationInput.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                durationInput.style.color = 'white';
                durationInput.style.width = '60px';
                durationInput.style.textAlign = 'center';
                durationInput.style.padding = '3px';
                durationInput.addEventListener('change', function(event) {
                    selectedImage.duration = parseInt(event.target.value);
                    updateTimeline();
                });

                formElement.appendChild(durationInput);
                formContainer.appendChild(formElement);
                timeline.appendChild(formContainer);
            }
        });
    }
}

function updateAudioTimeline() {
    timelineAudios.innerHTML = '';
    if (selectedAudios && selectedAudios.length > 0) {
        selectedAudios.forEach(selectedAudio => {
            if (selectedAudio && selectedAudio.src) {
                const audioContainer = document.createElement('div');
                audioContainer.classList.add('timeline-audio', 'p-2', 'bg-red-500', 'rounded-xl');
                audioContainer.style.minWidth = '100px'; // Set the minimum width here
                audioContainer.style.width = `${selectedAudio.duration * 100}px`;

                const audioForm = document.createElement('form');
                audioForm.style.padding = '0px';
                audioForm.style.borderRadius = '5px';
                audioForm.style.textAlign = 'center';
                audioForm.style.alignItems = 'center';

                const audioName = document.createElement('p');
                audioName.textContent = selectedAudio.name; // Add the audio name here
                audioName.style.textAlign = 'center';
                audioName.style.margin = 'auto'; // Center text horizontally

                const durationInput = document.createElement('input');
                durationInput.type = 'number';
                durationInput.min = 1;
                durationInput.value = selectedAudio.duration;
                durationInput.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
                durationInput.style.color = 'white';
                durationInput.style.width = '60px';
                durationInput.style.textAlign = 'center';
                durationInput.style.padding = '3px';
                durationInput.addEventListener('change', function(event) {
                    selectedAudio.duration = parseInt(event.target.value);
                    updateAudioTimeline();
                });

                audioForm.appendChild(durationInput);
                audioContainer.appendChild(audioForm);
                audioContainer.appendChild(audioName); // Append the audio name element
                timelineAudios.appendChild(audioContainer);
            }
        });
    }
}


// Function to send selected images and audios data to Python backend
function sendSelectedImagesAndAudiosToPython() {
    if (selectedImages.length > 0 || selectedAudios.length > 0) {
        const xhr = new XMLHttpRequest();
        const url = 'http://127.0.0.1:5000/receive-images';
        const data = JSON.stringify({ images: selectedImages, audios: selectedAudios, transition: transitionSelect.value, resolution: resolutionSelect.value });

        xhr.open('POST', url, true);
        xhr.setRequestHeader('Content-Type', 'application/json');

        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    console.log('Selected data sent successfully to Python backend.');
                } else {
                    console.error('Failed to send selected data to Python backend.');
                }
            }
        };

        xhr.send(data);
    }
}

// Attach event listeners to images in the container
const images = document.querySelectorAll('.image');
images.forEach(image => {
    image.addEventListener('click', toggleImageSelection);
});

// Attach event listeners to audio elements in the container
document.addEventListener('DOMContentLoaded', function() {
    // Attach event listener to the parent list item of audio elements
    const audioList = document.getElementById('audio-list');
    audioList.addEventListener('click', function(event) {
        const audio = event.target.closest('li'); // Get the parent list item
        if (audio && audio.querySelector('audio')) {
            toggleAudioSelection(audio); // Pass the parent list item to the function
        }
    });
});

// Add event listener to the "Create a Video" button
document.addEventListener('DOMContentLoaded', function() {
    // Get a reference to the "Create a Video" button
    const createVideoButton = document.querySelector('.create-video-button');

    // Add an event listener to the "Create a Video" button
    createVideoButton.addEventListener('click', function() {
        // Call the function to send selected images data to Python backend
        sendSelectedImagesAndAudiosToPython()
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
    selectedImages = [];
    selectedAudios = [];
    const selectedImageElements = document.querySelectorAll('.image.selected');
    const selectedAudioElements = document.querySelectorAll('audio.selected');
    selectedImageElements.forEach(image => {
        image.classList.remove('selected');
    });
    selectedAudioElements.forEach(audio => {
        audio.classList.remove('selected');
    });
    updateTimeline();
    updateAudioTimeline();
}

document.addEventListener('DOMContentLoaded', function() {
    const clearSelectionButton = document.getElementById('clear-selection');

    clearSelectionButton.addEventListener('click', function() {
        clearSelection();
    });
});

// Function to toggle the display of the audio list
function toggleAudioList() {
    var audioList = document.getElementById("audio-list");
    var audioContainer = document.getElementById("audio-list-container");
    if (audioList.style.display === "none") {
        audioList.style.display = "block";
        audioContainer.style.height = "200px";
    } else {
        audioList.style.display = "none";
        audioContainer.style.height = "fit-content"; // or any other default height you prefer
    }
}
