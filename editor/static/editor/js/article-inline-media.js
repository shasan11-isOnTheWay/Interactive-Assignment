(function () {
  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, '&#096;');
  }

  window.buildInlineMediaMarkup = function buildInlineMediaMarkup(item, icons) {
    if (!item || !item.id) return '';

    var type = item.media_type || 'text';
    var title = escapeHtml(item.title || 'Untitled');
    var icon = (icons && icons[type]) || '📎';
    var mediaId = escapeAttr(item.id);
    var fileUrl = escapeAttr(item.file_url || '');

    if (type === 'image' && fileUrl) {
      return '<span class="inline-media-link inline-media-embed inline-media-image" contenteditable="false" data-media-id="' + mediaId + '" data-media-type="' + escapeAttr(type) + '"><img src="' + fileUrl + '" alt="' + title + '"><span class="inline-media-meta">' + icon + ' ' + title + '</span></span>&nbsp;';
    }

    if ((type === 'audio' || type === 'video') && fileUrl) {
      return '<span class="inline-media-link inline-media-embed inline-media-' + escapeAttr(type) + '" contenteditable="false" data-media-id="' + mediaId + '" data-media-type="' + escapeAttr(type) + '"><span class="inline-media-badge">' + icon + '</span><span class="inline-media-meta">' + title + '</span></span>&nbsp;';
    }

    return '<span class="inline-media-link" contenteditable="false" data-media-id="' + mediaId + '" data-media-type="' + escapeAttr(type) + '">' + icon + ' ' + title + '</span>&nbsp;';
  };
})();
