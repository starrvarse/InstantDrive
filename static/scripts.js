// Show and Hide Forms for Adding Folders and Files
document.getElementById('add-folder-btn').addEventListener('click', function() {
    document.getElementById('folder-form').style.display = 'block';
    document.getElementById('files-form').style.display = 'none';
});

document.getElementById('add-files-btn').addEventListener('click', function() {
    document.getElementById('folder-form').style.display = 'none';
    document.getElementById('files-form').style.display = 'block';
});

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('folder-form').style.display = 'none';
    document.getElementById('files-form').style.display = 'none';
});

// Handle file upload with progress bar and upload speed
document.querySelector('#files-form form').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData(this);
    var xhr = new XMLHttpRequest();

    xhr.open('POST', this.action, true);

    xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
            var percentComplete = (e.loaded / e.total) * 100;
            document.getElementById('progressBar').style.width = percentComplete + '%';

            // Calculate upload speed in MB/s
            var uploadSpeed = (e.loaded / 1024 / 1024 / (e.timeStamp / 1000)).toFixed(2); // MB/s
            document.getElementById('uploadSpeed').textContent = 'Speed: ' + uploadSpeed + ' MB/s';
        }
    });

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    alert(response.message); // Show success message
                    window.location.reload(); // Refresh the page
                } else {
                    alert('Error: ' + response.message); // Show error message
                }
            } else {
                alert('An error occurred while uploading the file.');
            }
        }
    };

    document.getElementById('progressContainer').style.display = 'block';
    xhr.send(formData);
});

// Share Modal Logic
function showShareModal(event, itemPath) {
    event.preventDefault();

    var modal = document.getElementById('shareModal');
    modal.style.display = 'block';

    var shareLink = document.getElementById('shareLink');
    shareLink.value = window.location.origin + '/shared/' + btoa(itemPath);

    var shareForm = document.getElementById('shareForm');
    shareForm.action = '/generate_link/' + encodeURIComponent(itemPath);
}

function closeShareModal() {
    document.getElementById('shareModal').style.display = 'none';
}

// Copy share link to clipboard
function copyToClipboard() {
    var copyText = document.getElementById('shareLink');
    copyText.select();
    navigator.clipboard.writeText(copyText.value).then(function() {
        alert('Copied to clipboard: ' + copyText.value);
    });
}

// Handle the submission of share form (with options "Anyone with the link" or "Restricted")
document.getElementById('shareForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData(this);
    var xhr = new XMLHttpRequest();

    xhr.open('POST', this.action, true);

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            document.getElementById('shareLink').value = response.link; // Update the share link in the modal
            alert('Shareable link generated!');
        }
    };

    xhr.send(formData);
});
// Show success modal after file upload
function showSuccessModal() {
    var modal = document.getElementById('successModal');
    modal.style.display = 'block';
}

// Close the success modal
function closeSuccessModal() {
    var modal = document.getElementById('successModal');
    modal.style.display = 'none';
}

// Update the upload function to show the custom modal instead of alert
document.querySelector('#files-form form').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData(this);
    var xhr = new XMLHttpRequest();

    xhr.open('POST', this.action, true);

    xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
            var percentComplete = (e.loaded / e.total) * 100;
            document.getElementById('progressBar').style.width = percentComplete + '%';
        }
    });

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById('progressContainer').style.display = 'none';
            showSuccessModal();  // Show success modal on upload completion
        }
    };

    document.getElementById('progressContainer').style.display = 'block';
    xhr.send(formData);
});
