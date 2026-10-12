// draw 4 charts and write an insight

const COLORS = {
     dark: "#2b2b2b",
  yellow: "#f5b700",
  amber: "#e09b00",
  grey: "#8a8378",
  light: "#c9c1b3",
  grid: "#efeae0",
};

const DAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const DAY_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday",
  "Friday", "Saturday", "Sunday"];


  // small helpers

  function formatNumber(n){
    return Number(n).toLocaleString("en-US");
  }

  function shortNumber(value) {
    return value >= 1000 ? `${value / 1000}k` : value;
  }

  function formatHour(hour) {
    return `${String(hour).padStart(2, "0")}:00`;
  }

  function pick(rows, field, wantBiggest) {
  return rows.reduce((best, row) => {
    const better = wantBiggest ? row[field] > best[field] : row[field] < best[field];
    return better ? row : best;
  });
}

// charts
const charts = {
    instances: {},
    setup() {
        Chart.defaults.font.family = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
        Chart.defaults.color = "#6b6458";
    },
    // draw and replace what is already there
    draw(canvasId, config) {
    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
    }
    const canvas = document.getElementById(canvasId);
    this.instances[canvasId] = new Chart(canvas, config);
  },
  setInsight(id, text) {
    document.getElementById(id).textContent = text;
  },
  hourly(rows) {
    if (rows.length === 0) return;

    this.draw("chart-hourly", {
      data: {
        labels: rows.map((r) => String(r.hour).padStart(2, "0")),
        datasets: [
          {
            type: "bar",
            label: "Trips",
            data: rows.map((r) => r.trips),
            backgroundColor: COLORS.dark,
            borderRadius: 3,
            yAxisID: "y",
          },
          {
            type: "line",
            label: "Avg speed (mph)",
            data: rows.map((r) => r.avg_speed_mph),
            borderColor: COLORS.amber,
            backgroundColor: COLORS.amber,
            borderWidth: 2.5,
            pointRadius: 0,
            tension: 0.3,
            yAxisID: "y1",
          },
        ],
      },
      options: {
        interaction: { mode: "index", intersect: false },
        plugins: { legend: { position: "bottom", labels: { boxWidth: 12 } } },
        scales: {
          x: {
            grid: { display: false },
            title: { display: true, text: "Pickup hour" },
          },
          y: {
            grid: { color: COLORS.grid },
            ticks: { callback: shortNumber },
            title: { display: true, text: "Trips" },
          },
          y1: {
            position: "right",
            beginAtZero: true,
            grid: { display: false },
            title: { display: true, text: "mph" },
          },
        },
    },
});
const busiest = pick(rows, "trips", true);
    const slowest = pick(rows, "avg_speed_mph", false);
    const fastest = pick(rows, "avg_speed_mph", true);
    this.setInsight(
      "insight-hourly",
      `Busiest hour: ${formatHour(busiest.hour)} ` +
        `(${formatNumber(busiest.trips)} trips). ` +
        `Traffic is slowest at ${formatHour(slowest.hour)} ` +
        `(${slowest.avg_speed_mph} mph) and fastest at ` +
        `${formatHour(fastest.hour)} (${fastest.avg_speed_mph} mph).`
    );
  },
  topZones(rows) {
    if (rows.length ===0) return ;
    const isAirport = (r) => r.zone_name.includes("Airport");

    this.draw("chart-top-zones", {
      type: "bar",
      data: {
        labels: rows.map((r) => r.zone_name),
        datasets: [
          {
            label: "Pickups",
            data: rows.map((r) => r.trips),
            backgroundColor: rows.map((r) =>
              isAirport(r) ? COLORS.yellow : COLORS.dark
            ),
            borderRadius: 3,
          },
        ],
      },
      options : {
        indexAxis: "y",
        plugins:{
         legend: { display: false },
          tooltip: {
            callbacks: { afterLabel: (ctx) => rows[ctx.dataIndex].borough_name },
          },
        },
        scales: {
          x: { grid: { color: COLORS.grid }, ticks: { callback: shortNumber } },
          y: { grid: { display: false } },
        },
      },
    });
    const top = rows[0];
    const inManhattan = rows.filter((r) => r.borough_name === "Manhattan").length;
    const airports = rows.filter(isAirport).length;
    let text =
      `${top.zone_name} is the busiest pickup zone ` +
      `(${formatNumber(top.trips)} trips). ` +
      `${inManhattan} of the top ${rows.length} are in Manhattan`;
    if (airports > 0) {
      text += airports === 1
        ? ", and 1 is an airport (in yellow)."
        : `, and ${airports} are airports (in yellow).`;
    } else {
      text += ".";
    }
    this.setInsight("insight-top-zones", text);
  },

  weekday(rows) {
    if (rows.length === 0) return;
    const counts = DAY_SHORT.map(() => 0);
    rows.forEach((r) => {
      counts[r.weekday] = r.trips;
    });
 
    this.draw("chart-weekday", {
      type: "bar",
      data: {
        labels: DAY_SHORT,
        datasets: [
          {
            label: "Trips",
            data: counts,
            // weekends in yellow
            backgroundColor: DAY_SHORT.map((_, i) =>
              i >= 5 ? COLORS.yellow : COLORS.dark
            ),
            borderRadius: 3,
          },
        ],
      },
      options : {
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: COLORS.grid }, ticks: { callback: shortNumber } },
        },
      },
    });
     const busiest = counts.indexOf(Math.max(...counts));
    let text =
      `${DAY_FULL[busiest]} is the busiest day ` +
      `(${formatNumber(counts[busiest])} trips). Weekends are in yellow.`;
    if (rows.length < 7) {
      text += ` Only ${rows.length} of 7 days have trips in the loaded data, ` +
        "so this view is incomplete.";
    }
    this.setInsight("insight-weekday", text);
  },

  // how riders pay
  payment(rows) {
    if (rows.length === 0) return; 
     const palette = [COLORS.yellow, COLORS.dark, COLORS.grey, COLORS.light];
 
    this.draw("chart-payment", {
      type: "bar",
      data: {
        labels: rows.map((r) => r.payment_type),
        datasets: [
          {
            label: "Trips",
            data: rows.map((r) => r.trips),
            backgroundColor: rows.map((_, i) => palette[i % palette.length]),
            borderRadius: 3,
          },
        ],
      },
      options: {
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterLabel: (ctx) => {
                const tip = rows[ctx.dataIndex].avg_tip_pct;
                return tip === null ? "Tips not recorded" : `Average tip: ${tip}%`;
              },
            },
          },
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: COLORS.grid }, ticks: { callback: shortNumber } },
        },
      },
    });
     const total = rows.reduce((sum, r) => sum + r.trips, 0);
    const card = rows.find((r) => r.payment_type === "Credit card");
    if (card) {
      const share = ((card.trips / total) * 100).toFixed(1);
      this.setInsight(
        "insight-payment",
        `${share}% of trips are paid by credit card, with an average tip of ` +
          `${card.avg_tip_pct}%. Cash tips are not recorded, so cash shows no tip %.`
      );
    }
  },
};

