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
                } else {
                    $('#downloadButton').hide();
                }

                // Hide progress bar
                $('#progressBar').hide();
                $('#uploadForm button, #decryptForm button').prop('disabled', false);
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

        // Show progress bar if there are files selected
        if ($('#fileInput')[0].files.length > 0) {
            $('#progressBar').show();
            $('#uploadForm button').prop('disabled', true);
        }

        // Iterate over each file selected by the user
        const files = $('#fileInput')[0].files;
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            // Read the file contents
            const reader = new FileReader();
            reader.onload = function (event) {
                const fileData = event.target.result;

                // Encrypt the file data using the selected encryption algorithm
                const encryptedData = encryptFileData(fileData, encryption);

                // Upload the encrypted file block by block
                uploadFileBlockByBlock(file.name, encryptedData);
            };
            reader.readAsArrayBuffer(file);
        }
    });

    // Function to encrypt file data using the selected encryption algorithm, encryptionKey should be replaced with the actual encryption Key
    function encryptFileData(fileData, algorithm, encryptionKey) {
        // Convert the file data to a WordArray
        const wordArray = CryptoJS.lib.WordArray.create(fileData);

        // Encrypt the file data using the selected algorithm and encryption key
        let encryptedData;
        switch (algorithm) {
            case 'AES':
                encryptedData = CryptoJS.AES.encrypt(wordArray, encryptionKey).toString();
                break;
            case 'Salsa20':
                encryptedData = CryptoJS.Salsa20.encrypt(wordArray, encryptionKey).toString();
                break;
            default:
                console.error('Unsupported algorithm:', algorithm);
                encryptedData = null;
                break;
        }

        return encryptedData;
    }

    // Function to upload encrypted file block by block
    function uploadFileBlockByBlock(filename, encryptedData) {
        // Determine block size and number of blocks
        const blockSize = 1048576; // 1 MB
        const totalBlocks = Math.ceil(encryptedData.byteLength / blockSize);

        // Initialize block index
        let blockIndex = 0;

        // Define function to handle block upload
        function uploadNextBlock() {
            // Calculate start and end bytes for the current block
            const startByte = blockIndex * blockSize;
            const endByte = Math.min(startByte + blockSize, encryptedData.byteLength);
            const blockData = encryptedData.slice(startByte, endByte);

            // Send AJAX request to upload the current block
            $.ajax({
                url: '/upload',
                type: 'POST',
                data: {
                    filename: filename,
                    blockIndex: blockIndex,
                    totalBlocks: totalBlocks,
                    blockData: blockData
                },
                success: function (response) {
                    // Increment block index and check if there are more blocks to upload
                    blockIndex++;
                    if (blockIndex < totalBlocks) {
                        // Upload the next block
                        uploadNextBlock();
                    } else {
                        // All blocks uploaded successfully
                        console.log('Upload complete for file: ' + filename);
                        refreshDownloadLinks();
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Upload failed:', error);
                }
            });
        }

        // Start uploading the first block
        uploadNextBlock();
    }

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
            url: '/download',
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