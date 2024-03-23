$(document).ready(function () {
    // Function to refresh download links
    function refreshDownloadLinks() {
        // Send AJAX request to backend to get list of available files for download
        $.ajax({
            url: '/download',
            type: 'GET',
            success: function (response) {
                // Display download links
                $('#downloadLinks').html(response);

                // Show download button if there are any files
                if ($('#downloadLinks a').length > 0) {
                    $('#downloadButton').show();
                }

                // Hide progress bar
                $('#progressBar').hide();
                $('#uploadForm button, decryptForm button').prop('disabled', false);
            },
            error: function (xhr, status, error) {
                console.error('Failed to fetch download links:', error);
            }
        });
    }

    // Initial refresh of download links
    refreshDownloadLinks();

    // File upload form submission
    $('#uploadForm').submit(function (e) {
        e.preventDefault();

        // Get selected encryption algorithm
        const encryption = $('#encryption').val();

        // Show progress bar and disable upload button
        $('#progressBar').show();
        $('#uploadForm button').prop('disabled', true);

        // Send AJAX request to backend for file upload with encryption option
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: new FormData(this),
            contentType: false,
            processData: false,
            xhr: function () {
                const xhr = new window.XMLHttpRequest();

                xhr.upload.onprogress = function (event) {
                    if (event.lengthComputable) {
                        const percent = event.loaded / event.total * 100;
                        $('#progressBarInner').css('width', percent + '%');
                    }
                };

              return xhr;
            },
            success: function (response) {
                console.log('Upload successful:', response);
                refreshDownloadLinks();
            },
            error: function (xhr, status, error) {
                console.error('Upload failed:', error);
            },
            complete: function () {
                // Hide progress bar and enable upload button
                $('#progressBar').hide();
                $('#uploadForm button').prop('disabled', false);
            }
        });
    });

    // Decryption form submission
    $('#decryptForm').submit(function (e) {
        e.preventDefault();

        // Get filename to decrypt
        const filename = $('#fileToDecrypt').val();

        // Show progress bar and disable decrypt button
        $('#progressBar').show();
        $('#decryptForm button').prop('disabled', true);

        // Send AJAX request to backend for decryption
        $.ajax({
            url: '/decrypt',
            type: 'POST',
            data: { filename: filename },
            success: function (response) {
                console.log('Decryption successful:', response);
                refreshDownloadLinks();
            },
            error: function (xhr, status, error) {
                console.error('Decryption failed:', error);
            },
            complete: function () {
                // Hide progress bar and enable decrypt button
                $('#progressBar').hide();
                $('#decryptForm button').prop('disabled', false);
            }
        });
    });

    // Download button click event
    $(document).on('click', '#downloadButton', function () {
        // Send AJAX request to backend to initiate file download
        $.ajax({
            url: '/download',
            type: 'GET',
            success: function (response) {
                // Handle file download or display message
            },
            error: function (xhr, status, error) {
                console.error('Failed to initiate download:', error);
            }
        });
    });

    // Functions for start, pause, and resume buttons
    $('#startButton').click(function () {
        console.log('Start button clicked');
        // Send AJAX request to backend to start encryption
    });

    $('#pauseButton').click(function () {
        console.log('Pause button clicked');
        // Send AJAX request to backend to pause encryption
    });

    $('#resumeButton').click(function () {
        console.log('Resume button clicked');
        // Send AJAX request to backend to resume encryption
    });
});