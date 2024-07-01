// static/your_app/js/video_progress.js

document.addEventListener('DOMContentLoaded', function() {
    const video = document.querySelector('video');
    const courseId = document.getElementById('course-id').value;
    const progressUrl = `/courses/${courseId}/progress/`;

    if (video) {
        video.addEventListener('timeupdate', function() {
            const progress = (video.currentTime / video.duration) * 100;
            
            fetch(progressUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ progress: progress })
            })
            .then(response => response.json())
            .then(data => {
                if (data.certificate_url) {
                    // Optionally redirect to the certificate page
                    window.location.href = data.certificate_url;
                }
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
