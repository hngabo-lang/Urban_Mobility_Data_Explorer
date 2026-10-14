// starts the dashboard and connects all the parts, loadss in index.html: api.js, filter.js,
//  chart.js, map.js, then main.js (last, because it uses all the others)

// things the trips table need to remember
const state = {
    filters: {},
    sort: "pickup_datetime",
    order: "desc",
    page: 1,
    pageSize: 25,
    totalPages: 1,
};

// short way to find an element by its id
const $ = (id) => document.getElementById(id);

// ---formatting helpers----
function money(value) {
    if (value === null || value === undefined) return "-";
    return `$${Number(value).toFixed(2)}`;
    }

function percent(value){
    if (value === null || value === undefined) return "-";
    return `${Number(value).toFixed(1)}%`;
}

 // "2019-01-04 00:46:17" -> :="2019-01-04 00:46"
 function shortTime(datetime) {
    if (!datetime) return "-";
    return datetime.slice(0, 16);
 }

 // a table row with one message across all 8 columns
 function messageRow(text){
    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan =  8;
    cell.textContent = text;

    row.append(cell);
    return row;
     }
    
// -------1. summary cards------

async function loadSummary() {
    const s = await api.summary();

    $("stat-total").textContent = formatNumber(s.total_trips);
    $("stat-fare").textContent = money(s.avg_fare);
    $("stat-distance").textContent = `${s.avg_distance} mi`;
    $("stat-duration").textContent = `${s.avg_duration_min} min`;
    $("stat-speed").textContent = `${s.avg_speed_mph} mph`;
    $("stat-airport").textContent = `${s.airport_share_pct}%`;
    $("stat-cross").textContent = `${s.cross_borough_share_pct}%`;
    }
 
//-----2 chart-----

async function loadCharts() {
    charts.setup();
    // ask for all 4 at the same time instead of one after another
    const [hourly, topZones, weekday, payment] = await Promise.all([
        api.hourly(),
        api.topZones(10),
        api.weekday(),
        api.payment(),
    ]);
    charts.hourly(hourly);
    charts.topZones(topZones);
    charts.weekday(weekday);
    charts.payment(payment);
    }

    // -----3 map----

    async function loadMap() {
        if (typeof map === "undefined") return; // map.js not writter yet
       const [shapes, activity] = await Promise.all([
        api.zoneShapes(),
        api.zoneActivity(),
    ]);

    map.draw(shapes, activity);
}

// -----4 trips table----

async function loadTrips() {
  const body = $("trips-body");
  body.replaceChildren(messageRow("loading trips..."));

  const params = {
    ...state.filters,
    sort: state.sort,
    order: state.order,
    page: state.page,
    page_size: state.pageSize,
  };

  try{
    const data = await api.trips(params);
    
    state.totalPages = Math.max(data.total_pages, 1);
    renderTrips(data.trips);
    $("trips-count").textContent = 
      `${formatNumber(data.total)} trips match`;
    $("page-info").textContent =
      `page ${formatNumber(data.page)} of ${formatNumber(state.totalPages)}`;
  } catch (err) {
    body.replaceChildren(
      messageRow(`could not load trips: ${err.message}`)
    );
      state.totalPages = 1;
}

$("prev-page").disabled = state.page <= 1;
$("next-page").disabled = state.page >= state.totalPages;
}

function renderTrips(trips) {
    const body = $("trips-body");
    body.replaceChildren();

    if (trips.length === 0){
    body.append(messageRow("No trips match these filters."));
    return;
    } 

    for (const trip of trips) {
        const row = document.createElement("tr");
        const cells = [
            shortTime(trip.pickup_datetime),
            trip.pickup_zone,
            trip.dropoff_zone,
            `${trip.trip_distance.toFixed(2)} mi`,
            `${trip.trip_duration_min.toFixed(1)} min`,
            money(trip.fare_amount),
            percent(trip.tip_pct),
            money(trip.total_amount),
        ];
        for (const text of cells) {
            const cell = document.createElement("td");
            cell.textContent = text; //textcontent is safe: it never runs html
            row.append(cell);
        }
        row.addEventListener("click", () => showTrip(trip.trip_id));
        body.append(row);
    }
}

// -----5 sorting (click a column header)---

function setupSorting() {
    document.querySelectorAll("th[data-sort]").forEach((header) => {
        header.addEventListener("click", () => {
            const column = header.dataset.sort;
           
            if (state.sort === column) {
                // same column again: flip the direction
                state.order = state.order === "asc" ? "desc" : "asc";
            } else {
                state.sort = column;
                state.order = "desc";

            }
            state.page = 1;
            updateSortArrows();
            loadTrips();
        });
    });

updateSortArrows();
}

// adds .sort-asc or .sort-desc so styles.css can show the arrow
function updateSortArrows() {
    document.querySelectorAll("th[data-sort]").forEach((header) => {
        header.classList.remove("sort-asc", "sort-desc");

        if (header.dataset.sort === state.sort) {
            header.classList.add(`sort-${state.order}`);
        }
    });
}

// ------6 paging -----

function setupPaging() {
    $("prev-page").addEventListener("click", () => {
        if (state.page > 1) {
            state.page -= 1;
            loadTrips();
        
        }
    });

    $("next-page").addEventListener("click", () =>{
        if (state.page < state.totalPages) {
            state.page += 1;
            loadTrips();
        }
 });
}

// ------7 trip detail popup-------------

// [label, functiopn that gets the value from the trip]
const DETAIL_FIELDS = [
    ["Pickup", (t) => t.pickup_datetime],
    ["Dropoff", (t) => t.dropoff_datetime],
    ["From", (t) => `${t.pickup_zone} (${t.pickup_borough})`],
    ["To", (t) => `${t.dropoff_zone} (${t.dropoff_borough})`],
    ["Distance", (t) => `${t.trip_distance} mi`],
    ["Duration", (t) => `${t.trip_duration_min} min`],
    ["Average speed", (t) => `${t.avg_speed_mph} mph`],
    ["Passengers", (t) => t.passenger_count],
    ["Fare", (t) => money(t.fare_amount)],
    ["Tip", (t) => `${money(t.tip_amount)} (${percent(t.tip_pct)})`],
    ["Tolls", (t) => money(t.tolls_amount)],
    ["Total", (t) => money(t.total_amount)],
    ["Fare per mile", (t) => money(t.fare_per_mile)],
    ["Payment", (t) => t.payment_type],
    ["Rate code", (t) => t.rate_code],
    ["Vendor", (t) => t.vendor_name],
    ["Airport trip", (t) => (t.is_airport_trip ? "Yes" : "No")],
    ["Cross-borough", (t) => (t.is_cross_borough ? "Yes" : "No")],
    
];

async function showTrip(tripId) {
    const list = $("trip-detail-body");
    list.replaceChildren();

    try{
        const trip = await api.trip(tripId);
        for (const [label, getValue] of DETAIL_FIELDS){
            const term =  document.createElement("dt");
            term.textContent = label;
            const value = document.createElement("dd");
            value.textContent = getValue(trip);
            list.append(term, value);

        }
    } catch (err){
        list.textContent = `could not load trip ${tripId}: ${err.message}`;

    }
    $("trip-detail").showModal();
}

function setupDetail() {
    const dialog = $("trip-detail");
    $("close-detail").addEventListener("click", () => dialog.close());
    // clicking the dark area outside the popup also closes it
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) dialog.close();
    });

}

// -------8 start everything----------

async function start() {
    filters.fillHours();
    setupSorting();
    setupPaging();
    setupDetail();
    // when apply or reset is clicked: new filters, back to page 1
    filters.onChange((params) => {
        state.filters = params;
        state.page = 1;
        loadTrips();
    });

    loadTrips();

    // each part loads on its own, so one failure doesn't stop the others
    const results = await Promise.allSettled([
        api.boroughs().then((boroughs) => filters.fillBoroughs(boroughs)),
        loadSummary(),
        loadCharts(),
        loadMap(),
    ]);

    results.forEach((result) => {
        if (result.status === "rejected") {
            console.error(result.reason);
    }
    });

}
start();
