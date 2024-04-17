var timer;
var isPlaying = false;

function toggleTimer() {
    if (isPlaying) {
        clearInterval(timer);
        isPlaying = false;
        $('#playPauseBtn').html('<i class="bi bi-play-fill">');
    } else {
        timer = setInterval(function () {
            var timeLeft = parseInt($('#timer').text());
            if (timeLeft == 0) {
                $('#timer').text(60);
            } else {
                $('#timer').text(timeLeft - 1);
            }
        }, 1000);
        isPlaying = true;
        $('#playPauseBtn').html('<i class="bi bi-pause-fill">');
    }
}


$('#playPauseBtn').on("click", function () {
    toggleTimer();
});
