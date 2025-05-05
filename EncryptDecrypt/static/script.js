let currentOperationId = null;
let currentFile = null;
let currentAlgorithm = null;

// Utility to generate a unique operation ID
function generateOpId() {
    return 'op_' + Date.now() + '_' + Math.floor(Math.random() * 100000);
}

// Load file list from server
function refreshFileList() {
    $.ajax({
        url: '/files/list',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                let list = $('#fileList');
                list.empty();
                response.files.forEach(file => {
                    let li = $('<li>');
                    li.text(file.filename + ' (' + file.algorithm + ')');
                    let downloadBtn = $('<button>Download</button>').click(() => downloadFile(file.shadowname));
                    let decryptBtn = $('<button>Decrypt</button>').click(() => decryptFile(file.shadowname));
                    li.append(' ', downloadBtn, ' ', decryptBtn);
                    list.append(li);
                });
            }
        }
    });
}

// Upload file handler
$('#uploadForm').on('submit', function(e) {
    e.preventDefault();
    let fileInput = $('#fileInput')[0];
    if (!fileInput.files.length) return alert('Please select a file.');
    let file = fileInput.files[0];
    let algorithm = $('#algorithm').val();

    let formData = new FormData();
    formData.append('file', file);
    formData.append('algorithm', algorithm);

    $('#uploadBtn').prop('disabled', true).text('Uploading...');
    $.ajax({
        url: '/upload',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            $('#uploadBtn').prop('disabled', false).text('Upload');
            if (response.success) {
                alert('Upload successful!');
                refreshFileList();
                $('#decryptBtn').prop('disabled', false);
            } else {
                alert('Upload failed: ' + response.error);
            }
        },
        error: function() {
            $('#uploadBtn').prop('disabled', false).text('Upload');
            alert('Upload failed due to network/server error.');
        }
    });
});

// Download handler
function downloadFile(shadowname) {
    window.location = '/download/' + encodeURIComponent(shadowname);
}

// Decrypt handler (dummy, as actual decryption logic depends on backend/client-side crypto)
function decryptFile(shadowname) {
    alert('Decryption feature to be implemented as per your security model.');
}

// Start operation
$('#startBtn').on('click', function() {
    if (!currentOperationId) {
        currentOperationId = generateOpId();
    }
    $.ajax({
        url: '/operation/start',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ op_id: currentOperationId }),
        success: function(response) {
            if (response.success) {
                $('#pauseBtn').prop('disabled', false);
                $('#resumeBtn').prop('disabled', true);
                $('#progressContainer').show();
                pollProgress();
            }
        }
    });
});

// Pause operation
$('#pauseBtn').on('click', function() {
    if (!currentOperationId) return;
    $.ajax({
        url: '/operation/pause',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ op_id: currentOperationId }),
        success: function(response) {
            if (response.success) {
                $('#pauseBtn').prop('disabled', true);
                $('#resumeBtn').prop('disabled', false);
            }
        }
    });
});

// Resume operation
$('#resumeBtn').on('click', function() {
    if (!currentOperationId) return;
    $.ajax({
        url: '/operation/resume',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ op_id: currentOperationId }),
        success: function(response) {
            if (response.success) {
                $('#pauseBtn').prop('disabled', false);
                $('#resumeBtn').prop('disabled', true);
                pollProgress();
            }
        }
    });
});

// Poll operation progress
function pollProgress() {
    if (!currentOperationId) return;
    $.ajax({
        url: '/operation/progress',
        method: 'GET',
        data: { op_id: currentOperationId },
        success: function(response) {
            if (response.success) {
                let progress = response.progress || 0;
                $('#progressBar').val(progress);
                $('#progressText').text(progress + '%');
                if (!response.paused && progress < 100) {
                    setTimeout(pollProgress, 1000);
                } else if (progress >= 100) {
                    $('#pauseBtn').prop('disabled', true);
                    $('#resumeBtn').prop('disabled', true);
                    $('#progressContainer').hide();
                    alert('Operation completed!');
                }
            }
        }
    });
}

// Initial load
$(document).ready(function() {
    refreshFileList();
    $('#progressContainer').hide();
    $('#pauseBtn, #resumeBtn, #decryptBtn').prop('disabled', true);
});
