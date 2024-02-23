let dropArea = document.getElementById('drop-area');
      let imageGallery = document.getElementById('image-gallery');
      let uploadButton = document.getElementById('upload-btn');
      let filesToUpload = [];

      ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
          dropArea.addEventListener(eventName, preventDefaults, false);
      });

      function preventDefaults(e) {
          e.preventDefault();
          e.stopPropagation();
      }

      ['dragenter', 'dragover'].forEach(eventName => {
          dropArea.addEventListener(eventName, highlight, false);
      });

      ['dragleave', 'drop'].forEach(eventName => {
          dropArea.addEventListener(eventName, unhighlight, false);
      });

      function highlight() {
          dropArea.classList.add('highlight');
      }

      function unhighlight() {
          dropArea.classList.remove('highlight');
      }

      dropArea.addEventListener('drop', handleDrop, false);

      function handleDrop(e) {
          let dt = e.dataTransfer;
          let files = dt.files;

          handleFiles(files);
      }

      function handleFiles(files) {
          filesToUpload.push(...files);
          displayImages(files);
      }

      function displayImages(files) {
          files.forEach(file => {
              let img = document.createElement('img');
              img.classList.add('gallery-image');
              img.file = file;
              imageGallery.appendChild(img);

              let reader = new FileReader();
              reader.onload = (function(aImg) { return function(e) { aImg.src = e.target.result; }; })(img);
              reader.readAsDataURL(file);
          });
      }

      uploadButton.addEventListener('click', uploadFiles, false);

      function uploadFiles() {
          filesToUpload.forEach(uploadFile);
          filesToUpload = []; // Clear the files to upload array after upload
      }

      function uploadFile(file) {
          let formData = new FormData();
          formData.append('files', file);

          fetch('/upload', {
              method: 'POST',
              body: formData
          })
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok.');
              }
              return response.blob();
          })
          .then(blob => {
              // Handle the response if needed
              console.log('Image uploaded successfully');
          })
          .catch(error => console.error('Error uploading image:', error));
      }