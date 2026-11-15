let sigMap = null;
let rasterOverlays = [];

function showSection(sectionId, element) {
    // Nav items update
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    element.classList.add('active');

    // Sections update
    const sections = document.querySelectorAll('.theory-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    const activeSection = document.getElementById(sectionId);
    activeSection.classList.add('active');

    if (sectionId === 'dashboard' && sigMap) {
        setTimeout(() => sigMap.invalidateSize(), 200);
    }
}

function flyToTarget(lat, lon, zoom, btnElement) {
    if (btnElement) {
        document.querySelectorAll('.map-btn').forEach(btn => btn.classList.remove('active'));
        btnElement.classList.add('active');
    }
    if (sigMap) {
        sigMap.flyTo([lat, lon], zoom, { duration: 1.4 });
    }
}

function updateOverlayOpacity(val) {
    const label = document.getElementById('opacity-val');
    if (label) {
        label.textContent = Math.round(val * 100) + '%';
    }
    rasterOverlays.forEach(layer => {
        if (layer && typeof layer.setOpacity === 'function') {
            layer.setOpacity(parseFloat(val));
        }
    });
}

function renderMtInsarTable() {
    const tbody = document.getElementById('mt-insar-tbody');
    if (!tbody || typeof mtInsarData === 'undefined' || !mtInsarData.stats_table) return;

    tbody.innerHTML = '';
    mtInsarData.stats_table.forEach(row => {
        const ndviStr = row.mean_ndvi !== null ? `NDVI medio: <strong>${row.mean_ndvi.toFixed(3)}</strong>` : 'Alta montaña / Roca volcánica';
        const refStr = `[${row.ref_point.lat.toFixed(4)}°N, ${row.ref_point.lon.toFixed(4)}°W] (ASI=${row.ref_point.asi.toFixed(2)})`;

        // Fila PS
        const trPs = document.createElement('tr');
        trPs.innerHTML = `
            <td rowspan="2" style="font-weight: 600;">${row.zone}<br><span style="font-size: 0.78rem; color: var(--text-secondary);">${ndviStr}</span></td>
            <td><span class="badge-ps">PS (ASI &gt; 0.75)</span></td>
            <td rowspan="2">${row.theta_deg.toFixed(2)}°</td>
            <td><strong>${row.ps.CD.toLocaleString()}</strong> pts</td>
            <td>${row.ps.PV_LOS >= 0 ? '+' : ''}${row.ps.PV_LOS.toFixed(2)}</td>
            <td>±${row.ps.DV_LOS.toFixed(2)}</td>
            <td style="color: ${row.ps.VAA < -1 ? 'var(--accent-red)' : '#00d2ff'}; font-weight: 600;">${row.ps.VAA >= 0 ? '+' : ''}${row.ps.VAA.toFixed(2)}</td>
            <td>${row.ps.VEO >= 0 ? '+' : ''}${row.ps.VEO.toFixed(2)}</td>
            <td rowspan="2" style="font-size: 0.78rem; color: var(--text-secondary);">${refStr}</td>
        `;
        tbody.appendChild(trPs);

        // Fila SBAS
        const trSbas = document.createElement('tr');
        trSbas.innerHTML = `
            <td><span class="badge-sbas">SBAS (0.60 - 0.75)</span></td>
            <td><strong>${row.sbas.CD.toLocaleString()}</strong> pts</td>
            <td>${row.sbas.PV_LOS >= 0 ? '+' : ''}${row.sbas.PV_LOS.toFixed(2)}</td>
            <td>±${row.sbas.DV_LOS.toFixed(2)}</td>
            <td style="color: ${row.sbas.VAA < -1 ? 'var(--accent-red)' : '#ffcc00'}; font-weight: 600;">${row.sbas.VAA >= 0 ? '+' : ''}${row.sbas.VAA.toFixed(2)}</td>
            <td>${row.sbas.VEO >= 0 ? '+' : ''}${row.sbas.VEO.toFixed(2)}</td>
        `;
        tbody.appendChild(trSbas);
    });
}

function initSigMap() {
    const mapContainer = document.getElementById('sig-map');
    if (!mapContainer || typeof L === 'undefined') return;

    sigMap = L.map('sig-map', {
        center: [2.4010, -76.5700],
        zoom: 13,
        zoomControl: true
    });

    // Capas Base
    const esriSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Copernicus Sentinel-1/2',
        maxZoom: 19
    }).addTo(sigMap);

    const openTopo = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data: &copy; OpenStreetMap, SRTM | Map style: &copy; OpenTopoMap',
        maxZoom: 17
    });

    const cartoDark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 19
    });

    const baseMaps = {
        "Satélite Esri (Óptico Real)": esriSat,
        "Topográfico Curvas de Nivel (DEM)": openTopo,
        "Modo Oscuro Científico": cartoDark
    };

    const overlayMaps = {};

    // Superposiciones Ráster Georreferenciadas (Sentinel-1 y Sentinel-2 Actualizadas Nov 2026)
    if (typeof mtInsarData !== 'undefined' && mtInsarData.overlays) {
        const ov = mtInsarData.overlays;

        if (ov.samanga_rgb) {
            const lRgbSam = L.imageOverlay(ov.samanga_rgb.url, ov.samanga_rgb.bounds, { opacity: 0.85 });
            rasterOverlays.push(lRgbSam);
            overlayMaps["📸 " + ov.samanga_rgb.title] = lRgbSam;
        }
        if (ov.samanga_ndvi) {
            const lNdvi = L.imageOverlay(ov.samanga_ndvi.url, ov.samanga_ndvi.bounds, { opacity: 0.78 }).addTo(sigMap);
            rasterOverlays.push(lNdvi);
            overlayMaps["🌿 " + ov.samanga_ndvi.title] = lNdvi;
        }
        if (ov.samanga_asi) {
            const lAsi = L.imageOverlay(ov.samanga_asi.url, ov.samanga_asi.bounds, { opacity: 0.78 });
            rasterOverlays.push(lAsi);
            overlayMaps["📡 " + ov.samanga_asi.title] = lAsi;
        }
        if (ov.purace_rgb) {
            const lRgbPur = L.imageOverlay(ov.purace_rgb.url, ov.purace_rgb.bounds, { opacity: 0.90 }).addTo(sigMap);
            rasterOverlays.push(lRgbPur);
            overlayMaps["🏔️ " + ov.purace_rgb.title] = lRgbPur;
        }
        if (ov.purace_ifg) {
            const lPurace = L.imageOverlay(ov.purace_ifg.url, ov.purace_ifg.bounds, { opacity: 0.75 }).addTo(sigMap);
            rasterOverlays.push(lPurace);
            overlayMaps["🌋 " + ov.purace_ifg.title] = lPurace;
        }
        if (ov.sotara_sar) {
            const lSotara = L.imageOverlay(ov.sotara_sar.url, ov.sotara_sar.bounds, { opacity: 0.78 }).addTo(sigMap);
            rasterOverlays.push(lSotara);
            overlayMaps["⛰️ " + ov.sotara_sar.title] = lSotara;
        }
    }

    // Grupos Vectoriales PS, SBAS, Referencias e Hitos
    const psGroup = L.layerGroup().addTo(sigMap);
    const sbasGroup = L.layerGroup().addTo(sigMap);
    const refGroup = L.layerGroup().addTo(sigMap);
    const sgcGroup = L.layerGroup().addTo(sigMap);

    if (typeof mtInsarData !== 'undefined') {
        // Dispersores PS y SBAS
        if (mtInsarData.scatterers) {
            mtInsarData.scatterers.forEach(pt => {
                const isPs = pt.method === 'PS';
                const marker = L.circleMarker([pt.lat, pt.lon], {
                    radius: isPs ? 5.5 : 5,
                    fillColor: isPs ? '#00d2ff' : '#ffcc00',
                    color: '#0b0e14',
                    weight: 1.2,
                    opacity: 1,
                    fillOpacity: 0.9
                });

                const ndviInfo = pt.ndvi !== null ? `<br><strong>NDVI (Sentinel-2):</strong> ${pt.ndvi.toFixed(3)}` : '';
                marker.bindPopup(`
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.82rem; line-height: 1.45;">
                        <strong style="color: ${isPs ? '#00d2ff' : '#ffcc00'};">Dispersor ${pt.method} (${pt.zone})</strong><br>
                        <strong>Coordenadas:</strong> ${pt.lat.toFixed(5)}°N, ${pt.lon.toFixed(5)}°W<br>
                        <strong>Índice Estabilidad (ASI):</strong> ${pt.asi.toFixed(3)}<br>
                        <strong>Despl. LOS:</strong> ${pt.v_los >= 0 ? '+' : ''}${pt.v_los.toFixed(2)} mm<br>
                        <strong>Vertical (V<sub>AA</sub>):</strong> ${pt.v_aa >= 0 ? '+' : ''}${pt.v_aa.toFixed(2)} mm<br>
                        <strong>Este-Oeste (V<sub>EO</sub>):</strong> ${pt.v_eo >= 0 ? '+' : ''}${pt.v_eo.toFixed(2)} mm
                        ${ndviInfo}
                    </div>
                `);

                if (isPs) {
                    psGroup.addLayer(marker);
                } else {
                    sbasGroup.addLayer(marker);
                }
            });
        }

        // Puntos de Referencia Estable (APS = 0)
        if (mtInsarData.stats_table) {
            mtInsarData.stats_table.forEach(st => {
                if (st.ref_point) {
                    const refMarker = L.circleMarker([st.ref_point.lat, st.ref_point.lon], {
                        radius: 8,
                        fillColor: '#ffffff',
                        color: '#00d2ff',
                        weight: 3,
                        fillOpacity: 1
                    });
                    refMarker.bindPopup(`
                        <div style="font-family: 'Inter', sans-serif; font-size: 0.82rem;">
                            <strong style="color: #00d2ff;">★ Punto de Referencia Estable (Anclaje APS)</strong><br>
                            <strong>Zona:</strong> ${st.zone}<br>
                            <strong>Coordenadas:</strong> ${st.ref_point.lat.toFixed(5)}°N, ${st.ref_point.lon.toFixed(5)}°W<br>
                            <strong>ASI:</strong> ${st.ref_point.asi.toFixed(3)} (Fase de referencia = 0.0 mm)
                        </div>
                    `);
                    refGroup.addLayer(refMarker);
                }
            });
        }

        // Hitos Territoriales
        if (mtInsarData.landmarks) {
            mtInsarData.landmarks.forEach(lm => {
                const lmMarker = L.circleMarker([lm.lat, lm.lon], {
                    radius: 7,
                    fillColor: lm.type === 'community' ? '#00ff88' : (lm.type === 'sgc' ? '#00d2ff' : '#ff4b2b'),
                    color: '#ffffff',
                    weight: 2,
                    fillOpacity: 0.95
                });
                lmMarker.bindPopup(`
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.85rem;">
                        <strong>📍 ${lm.name}</strong><br>
                        Lat: ${lm.lat.toFixed(4)}°N | Lon: ${lm.lon.toFixed(4)}°W
                    </div>
                `);
                refGroup.addLayer(lmMarker);
            });
        }
    }

    // Eventos Sísmicos SGC
    if (typeof sgcData !== 'undefined' && sgcData) {
        sgcData.forEach(ev => {
            const attr = ev.attributes;
            if (attr.LATITUD && attr.LONGITUD) {
                const sMarker = L.circleMarker([attr.LATITUD, attr.LONGITUD], {
                    radius: Math.max(6, attr.MAGNITUD * 4.2),
                    fillColor: '#ff4b2b',
                    color: '#ffffff',
                    weight: 1.5,
                    fillOpacity: 0.85
                });
                sMarker.bindPopup(`
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.82rem;">
                        <strong style="color: #ff4b2b;">🔴 Sismo SGC - OVSPop</strong><br>
                        <strong>Lugar:</strong> ${attr.LUGAR}<br>
                        <strong>Magnitud:</strong> ${attr.MAGNITUD.toFixed(1)} ML | <strong>Prof:</strong> ${attr.PROFUNDIDAD || '--'} km<br>
                        <strong>Tipo:</strong> ${attr.TIPO || 'Volcano-Tectónico'}<br>
                        <strong>Fecha UTC:</strong> ${attr.FECHA_UTC}
                    </div>
                `);
                sgcGroup.addLayer(sMarker);
            }
        });
    }

    overlayMaps["🔵 Dispersores Persistentes (PS: ASI > 0.75)"] = psGroup;
    overlayMaps["🟡 Dispersores Distribuidos (SBAS: 0.60 - 0.75)"] = sbasGroup;
    overlayMaps["⭐ Puntos de Referencia (APS) e Hitos"] = refGroup;
    overlayMaps["🔴 Sismicidad SGC (OVSPop)"] = sgcGroup;

    L.control.layers(baseMaps, overlayMaps, { collapsed: false }).addTo(sigMap);
}

function renderSgcData() {
    const listContainer = document.getElementById('sgc-data-list');

    if (typeof sgcData !== 'undefined' && sgcData && sgcData.length > 0) {
        listContainer.innerHTML = '';
        sgcData.forEach(event => {
            const attr = event.attributes;
            const item = document.createElement('div');
            item.className = 'ticker-item';

            const magColor = attr.MAGNITUD >= 2.0 ? 'var(--accent-red)' : 'var(--text-primary)';
            const profInfo = attr.PROFUNDIDAD ? ` | Prof: ${attr.PROFUNDIDAD} km` : '';
            const tipoInfo = attr.TIPO ? ` (${attr.TIPO})` : '';

            item.innerHTML = `
                <div>
                    <span style="font-weight: 600; color: ${magColor}">${attr.LUGAR || 'Evento sísmico'}</span>
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">${tipoInfo}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.8rem;">
                    <span style="color: var(--text-secondary); font-size: 0.85rem;"><strong>${attr.MAGNITUD.toFixed(1)} ML</strong>${profInfo} — ${attr.FECHA_UTC}</span>
                    ${attr.LATITUD ? `<button class="map-btn" style="padding: 0.25rem 0.6rem; font-size: 0.75rem;" onclick="flyToTarget(${attr.LATITUD}, ${attr.LONGITUD}, 13)">Ver en SIG</button>` : ''}
                </div>
            `;
            listContainer.appendChild(item);
        });
    } else {
        listContainer.innerHTML = '<div class="ticker-item"><span>No hay eventos recientes o el archivo sgc_data.js no se ha cargado correctamente.</span></div>';
    }
}

// Initial Render
document.addEventListener('DOMContentLoaded', () => {
    console.log("Centro de Geodesia Satelital & Territorio — Samanga Baja Loaded.");
    renderSgcData();
    renderMtInsarTable();
    initSigMap();

    // Micro-animation for cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});

