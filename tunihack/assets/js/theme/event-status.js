// Fills [data-event-status] with "Starts in", "Live" or "Ended" from the CTF start/end times.
function formatDuration(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.max(1, Math.floor((seconds % 3600) / 60));
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

export default () => {
  const $el = document.querySelector("[data-event-status]");
  if (!$el) return;

  const start = Number(window.init.start) || null;
  const end = Number(window.init.end) || null;
  if (!start && !end) return;

  const render = () => {
    const now = Date.now() / 1000;
    let state;
    let text;
    if (start && now < start) {
      state = "upcoming";
      text = `Starts in ${formatDuration(start - now)}`;
    } else if (end && now >= end) {
      state = "ended";
      text = "This edition has ended";
    } else {
      state = "live";
      text = end ? `Live now · ends in ${formatDuration(end - now)}` : "Live now";
    }
    $el.dataset.state = state;
    $el.textContent = text;
    $el.hidden = false;
  };

  render();
  setInterval(render, 30000);
};
