/* Map pointer markers that use the FireRoute logo instead of plain red dots.
   kind: 'station' (dark red, gold ring) | 'incident' (bright red, pulsing) | 'origin' */
window.firePin = function (kind) {
  var logo = window.FIRE_LOGO_URL || '/static/dashboard/img/logo.svg';
  var cls = 'fire-pin fire-pin-' + (kind || 'station');
  var big = kind === 'incident';
  var w = big ? 44 : 38, h = big ? 54 : 47;
  return L.divIcon({
    className: 'fire-pin-wrap',
    html: '<div class="' + cls + '">' + (big ? '<span class="fire-pin-pulse"></span>' : '') +
      '<span class="fire-pin-head"><img src="' + logo + '" alt="" draggable="false"></span></div>',
    iconSize: [w, h],
    iconAnchor: [w / 2, h - 2],
    popupAnchor: [0, -h + 8],
    tooltipAnchor: [w / 2, -h / 2]
  });
};
