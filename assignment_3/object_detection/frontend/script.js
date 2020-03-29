$(document).ready(function () {
    $('#upload').on('click', function () {
        const formData = new FormData();
        const insertedLength = document.getElementById('file').files.length;
        if (insertedLength === 0) {
            $('#message').html('<span>Select at least one file</span>');
            return;
        }
        formData.append("files", document.getElementById('file').files[0]);
        $.ajax({
            type: 'POST',
            url: "http://127.0.0.1:5000/upload",
            dataType: 'text',
            cache: false,
            contentType: false,
            processData: false,
            data: formData,
            success: function (data, status, jqXHR) {
                $('#message').html('');
                const mimeType = jqXHR.getResponseHeader("content-type");
                $('#result').attr('src', `data:${mimeType};base64,${data}`);
            },
            error: function (data) {
                $('#message').html(data.responseText);
            }
        });
    });
});