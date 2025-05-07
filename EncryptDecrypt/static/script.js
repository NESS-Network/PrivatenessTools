$(document).ready(function() {
    let currentOperationId = null;
    let selectedFile = null;

    // Initialize file list
    refreshFileList();

    // File Upload Handler
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', $('#fileInput')[0].files[0]);
        formData.append('algorithm', $('#algorithm').val());
        formData.append('key', $('#encryptionKey').val());

        $('#uploadBtn').prop('disabled', true).text('Encrypting...');
        
        $.ajax({
            url: '/upload',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    alert('File encrypted successfully!');
                    refreshFileList();
                    $('#uploadForm')[0].reset();
                } else {
                    alert('Error: ' + response.error);
                }
            },
            error: function(xhr) {
                alert('Upload failed: ' + xhr.responseJSON.error);
            },
            complete: function() {
                $('#uploadBtn').prop('disabled', false).text('Upload & Encrypt');
            }
        });
    });

    // File List Click Handler
    $(document).on('click', '.file-item', function() {
        $('.file-item').removeClass('selected');
        $(this).addClass('selected');
        selectedFile = $(this).data('shadowname');
        $('#decryptSection').show();
    });

    // Download Handler
    $(document).on('click', '.download-btn', function() {
        const shadowname = $(this).closest('.file-item').data('shadowname');
        window.location = `/download/${encodeURIComponent(shadowname)}`;
    });

    // Decrypt Handler
    $('#decryptBtn').click(function() {
        const key = $('#decryptionKey').val();
        if (!key) {
            alert('Please enter decryption key');
            return;
        }

        $.ajax({
            url: `/decrypt/${selectedFile}`,
            method: 'POST',
            data: { key: key },
            success: function(response) {
                if (response.success) {
                    alert('Decryption successful!');
                    refreshFileList();
                } else {
                    alert('Decryption failed: ' + response.error);
                }
            },
            error: function(xhr) {
                alert('Decryption error: ' + xhr.responseJSON.error);
            }
        });
    });

    // Operation Controls
    $('#startBtn').click(startOperation);
    $('#pauseBtn').click(pauseOperation);
    $('#resumeBtn').click(resumeOperation);

    // Refresh file list every 30 seconds
    setInterval(refreshFileList, 30000);

    // Utility Functions
    function refreshFileList() {
        $.get('/files/list', function(response) {
            if (response.success) {
                const fileList = $('#fileList');
                fileList.empty();
                
                response.files.forEach(file => {
                    fileList.append(`
                        <div class="file-item" data-shadowname="${file.shadowname}">
                            <div class="file-info">
                                <span class="filename">${file.filename}</span>
                                <span class="algorithm">${file.algorithm}</span>
                            </div>
                            <button class="download-btn action-btn">Download</button>
                        </div>
                    `);
                });
            }
        });
    }

    function startOperation() {
        currentOperationId = `op_${Date.now()}`;
        $.post('/operation/start', { op_id: currentOperationId }, function(response) {
            if (response.success) {
                $('#pauseBtn').prop('disabled', false);
                $('#resumeBtn').prop('disabled', true);
                pollProgress();
            }
        });
    }

    function pauseOperation() {
        $.post('/operation/pause', { op_id: currentOperationId }, function(response) {
            if (response.success) {
                $('#pauseBtn').prop('disabled', true);
                $('#resumeBtn').prop('disabled', false);
            }
        });
    }

    function resumeOperation() {
        $.post('/operation/resume', { op_id: currentOperationId }, function(response) {
            if (response.success) {
                $('#pauseBtn').prop('disabled', false);
                $('#resumeBtn').prop('disabled', true);
                pollProgress();
            }
        });
    }

    function pollProgress() {
        $.get('/operation/progress', { op_id: currentOperationId }, function(response) {
            if (response.success) {
                $('#progressBar').val(response.progress);
                $('#progressText').text(response.progress + '%');
                
                if (!response.paused && response.progress < 100) {
                    setTimeout(pollProgress, 1000);
                } else if (response.progress >= 100) {
                    $('#pauseBtn').prop('disabled', true);
                    $('#resumeBtn').prop('disabled', true);
                }
            }
        });
    }
});
