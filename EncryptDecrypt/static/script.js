$(document).ready(function() {
    // Toggle RPC fields in nodes form
    $('input[name="mode"]').change(function() {
      if ($(this).val() === 'rpc') {
        $('#rpc-fields').show();
      } else {
        $('#rpc-fields').hide();
      }
    });
  
    // Handle task controls (example)
    $('.task-start').click(function() {
      const taskId = $(this).data('task-id');
      $.post(`/task/${taskId}/start`, function(res) {
        console.log('Started:', res);
      });
    });
    $('.task-pause').click(function() {
      const taskId = $(this).data('task-id');
      $.post(`/task/${taskId}/pause`, function(res) {
        console.log('Paused:', res);
      });
    });
    $('.task-resume').click(function() {
      const taskId = $(this).data('task-id');
      $.post(`/task/${taskId}/resume`, function(res) {
        console.log('Resumed:', res);
      });
    });
  
    // Example: poll progress
    function pollProgress(taskId) {
      $.get(`/task/${taskId}/progress`, function(res) {
        $(`#progress-${taskId}`).text(res.progress + '% - ' + res.status);
        if (res.status === 'running') setTimeout(() => pollProgress(taskId), 1000);
      });
    }
  });