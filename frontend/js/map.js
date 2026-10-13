const MAP_SHADES = ["#fff3c4","#ffe08a", "#f7c948", "#f0a500", "#c27c00", "#8a5300" ];
const NO_DATA_COLOR = "#e4ddd0";
const NYC_CENTER = [40.7128, -74.006];

const map = {
    leaflet: null,
    layer: null,
    legend: null,

    init() {
      if (this.leaflet) return; 
      this.leaflet = L.map("map", {
        scrollWheelZoom: false,
        maxBoundsViscosity: 1.0, // the edge of the allowed area is a solid wall
      }).setView(NYC_CENTER, 10);
      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        maxZoom: 19,
      }).addTo(this.leaflet); 
    },

    colorFor(pickups, maxPickups) {
        if (!pickups) return NO_DATA_COLOR;
        const ratio = Math.log10(pickups + 1) / Math.log10(maxPickups + 1);
        const level = Math.floor(ratio * MAP_SHADES.length);
        return MAP_SHADES[Math.min(level, MAP_SHADES.length - 1)];
    },

    popupFor(feature, pickups) {
        const box = document.createElement("div");
        const title = document.createElement("strong");
        title.textContent = feature.properties.zone;
        const details = document.createElement("div");
        details.textContent =
           `${feature.properties.borough} . ${formatNumber(pickups)} pickups`;
        box.append(title, details);
        return box;
    },

    draw(shapes, activity) {
        this.init();
    
        const pickupsByZone = {};
        activity.forEach((row) => {
          pickupsByZone[row.location_id] = row.pickups;
        });
        const maxPickups = Math.max(1, ...activity.map((row) => row.pickups));

        if (this.layer) this.layer.remove();

        this.layer = L.geoJSON(shapes,  {
            style: (feature) => ({
                fillColor: this.colorFor(pickupsByZone[feature.properties.location_id],
                    maxPickups),
                fillOpacity: 0.85,
                color: "#ffffff",
                weight: 0.6,
           }),
           onEachFeature: (feature, shape) => {
               const pickups = pickupsByZone[feature.properties.location_id] || 0;
               shape.bindPopup(this.popupFor(feature, pickups));
               shape.on("mouseover", () => shape.setStyle({ color: "#141414", weight: 2}));
               shape.on("mouseout", () => this.layer.resetStyle(shape));
           },
        }).addTo(this.leaflet);

        const bounds = this.layer.getBounds();
        this.leaflet.fitBounds(bounds);
        this.leaflet.setMaxBounds(bounds.pad(0.1));
        this.leaflet.setMinZoom(this.leaflet.getZoom());
        this.addLegend(maxPickups);
    },
    
     addLegend(maxPickups) {
        if (this.legend) this.legend.remove();
        this.legend = L.control({ position: "bottomright" });

        this.legend.onAdd = () => {
           const box = L.DomUtil.create("div");
           Object.assign(box.style, {
             background: "#ffffff",
             padding: "8px 10px",
             borderRadius: "6px",
             boxShadow: "0 1px 4px rgba(0, 0, 0, 0.2)",
             font: "12px system-ui, sans-serif",
             color: "#1c1c1c",           
        });
    
        const title = document.createElement("div");
        title.textContent = "Pickups (log scale)";
        title.style.fontWeight = "600";
        title.style.marginBottom = "4px";

        const bar = document.createElement("div");
        bar.style.display = "flex";
        MAP_SHADES.forEach((shade) => {
            const step = document.createElement("span");
            Object.assign(step.style, {
                width: "24px",
                height: "10px",
                background: shade,
            });
                bar.append(step);
         });

         const labels = document.createElement("div");
         labels.style.display = "flex";
         labels.style.justifyContent = "space-between";
         const low = document.createElement ("span");
         low.textContent = "Few";
         const high = document.createElement("span");
         high.textContent = formatNumber(maxPickups);
         labels.append(low, high);

         box.append(title, bar, labels);
         return box;
        };

        this.legend.addTo(this.leaflet);
    },
  }; 
