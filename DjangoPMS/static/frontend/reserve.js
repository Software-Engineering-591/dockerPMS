window.addEventListener(
  "map:init",
  function (e) {
    let detail = e.detail;
    let greenIcon = L.icon({
      iconUrl:
        "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
      shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
    });
    geo_data.forEach((d) => {
      L.marker(d.point, { icon: greenIcon })
        .bindPopup(d.popup_html, {
          className: "lot",
        })
        .addTo(detail.map);
      L.polygon(d.poly).addTo(detail.map);
    });
  },
  false,
);
