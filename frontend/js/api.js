const API_BASE = "http://127.0.0.1:5000/api";

async function fetchJSON(path) {
    const response = await fetch(`${API_BASE}${path}`);
    if (!response.ok){
        throw new Error(`API error ${response.status} on ${path}`);
    }
return response.json();
}


const api ={
    boroughs:() => fetchJSON("/boroughs"),
    zones:() => fetchJSON("/zones"),
    zoneShapes:() => fetchJSON("/zones/geojson"),
    trips:(params) =>
         fetchJSON(`/trips?${new URLSearchParams(params)}`),
    trip: (id) => fetchJSON(`/trips/${id}`),
    summary: () => fetchJSON("/insights/summary"),
    hourly: () => fetchJSON("/insights/hourly"),
    weekday: () => fetchJSON("/insights/weekday"),
    topZones: (limit = 10) =>
         fetchJSON(`/insights/top-zones?limit=${limit}`),
    zoneActivity: () => fetchJSON("/insights/zone-activity"),
    payment: () => fetchJSON("/insights/payment"),

};

