document.addEventListener("DOMContentLoaded", function() {
  const channelId = 'UC4jTx6TcenHTWW4XPqRPl6Q'; // @PhysicsVoyage channel ID
  const rssUrl = encodeURIComponent(`https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}`);
  const apiUrl = `https://api.rss2json.com/v1/api.json?rss_url=${rssUrl}`;

  fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      if (data.status === 'ok' && data.items.length > 0) {
        const latestVideo = data.items[0];
        
        // Extract video ID from link
        const videoIdMatch = latestVideo.link.match(/v=([^&]+)/);
        const videoId = videoIdMatch ? videoIdMatch[1] : null;

        if (videoId) {
          const iframeHtml = `
            <div class="ratio ratio-16x9 mb-2">
              <iframe 
                src="https://www.youtube.com/embed/${videoId}" 
                title="${latestVideo.title}" 
                allowfullscreen>
              </iframe>
            </div>
            <h6 class="card-title mb-1" style="font-weight: 600;">
              <a href="${latestVideo.link}" target="_blank" class="stretched-link text-decoration-none text-reset">
                ${latestVideo.title}
              </a>
            </h6>
            <small class="text-muted">Published: ${new Date(latestVideo.pubDate).toLocaleDateString()}</small>
          `;
          
          const container = document.getElementById("youtube-latest-video-container");
          if (container) {
            container.innerHTML = iframeHtml;
          }
        }
      }
    })
    .catch(error => console.error('Error fetching YouTube RSS:', error));
});
