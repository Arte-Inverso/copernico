let sigMap = null;
let rasterOverlays = [];
let sgcMarkers = [];
let sgcGroup = null;
let gnssGroup = null;
let currentSeismicFilter = 'ALL';

function showSection(sectionId, element) {
    // Nav items update
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    
    if (element) {
        element.classList.add('active');
    } else {
        const matchingNav = document.querySelector(`.nav-item[onclick*="'${sectionId}'"]`);
        if (matchingNav) matchingNav.classList.add('active');
    }

    // Sections update
    const sections = document.querySelectorAll('.theory-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    const activeSection = document.getElementById(sectionId);
    if (activeSection) {
        activeSection.classList.add('active');
    }

    if (sectionId === 'dashboard' && sigMap) {
        setTimeout(() => sigMap.invalidateSize(), 200);
    }
}

function flyToTarget(lat, lon, zoom, btnElement) {
    // 1. Asegurar que la pestaña de Mapa SIG & InSAR esté activa
    showSection('dashboard');

    // 2. Resaltar botón seleccionado si existe
    if (btnElement) {
        document.querySelectorAll('.map-btn').forEach(btn => btn.classList.remove('active'));
        btnElement.classList.add('active');
    }

    // 3. Desplazar suavemente la ventana hacia el contenedor del mapa
    const mapElement = document.getElementById('sig-map');
    if (mapElement) {
        mapElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // 4. Centrar mapa y abrir popup del evento sísmico o dispersor
    if (sigMap) {
        sigMap.invalidateSize();
        const targetZoom = zoom || 14;
        sigMap.flyTo([lat, lon], targetZoom, {
            duration: 1.2,
            easeLinearity: 0.25
        });

        // Asegurar que la capa sísmica esté visible en el mapa
        if (sgcGroup && !sigMap.hasLayer(sgcGroup)) {
            sigMap.addLayer(sgcGroup);
        }

        // 5. Localizar marcador correspondiente y abrir popup con animación de resalte
        setTimeout(() => {
            let found = false;
            if (sgcMarkers && sgcMarkers.length > 0) {
                for (const item of sgcMarkers) {
                    const dLat = Math.abs(item.lat - lat);
                    const dLon = Math.abs(item.lon - lon);
                    if (dLat < 0.005 && dLon < 0.005) {
                        item.layer.openPopup();
                        // Efecto de pulso en el marcador
                        const origRadius = item.layer.getRadius();
                        item.layer.setRadius(origRadius + 6);
                        item.layer.setStyle({ color: '#38bdf8', weight: 4 });
                        setTimeout(() => {
                            item.layer.setRadius(origRadius);
                            item.layer.setStyle({ color: '#ffffff', weight: 1.5 });
                        }, 1600);
                        found = true;
                        break;
                    }
                }
            }

            if (!found) {
                sigMap.eachLayer(layer => {
                    if (layer.getLatLng && layer.getPopup) {
                        const pos = layer.getLatLng();
                        if (Math.abs(pos.lat - lat) < 0.005 && Math.abs(pos.lng - lon) < 0.005) {
                            layer.openPopup();
                        }
                    }
                });
            }
        }, 1100);
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
        center: [2.317, -76.398], // Centrado en el edificio volcánico Puracé
        zoom: 12,
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

        if (ov.purace_rgb) {
            const lRgbPur = L.imageOverlay(ov.purace_rgb.url, ov.purace_rgb.bounds, { opacity: 0.90 }).addTo(sigMap);
            rasterOverlays.push(lRgbPur);
            overlayMaps["🌋 " + ov.purace_rgb.title] = lRgbPur;
        }
        if (ov.purace_ifg) {
            const lPurace = L.imageOverlay(ov.purace_ifg.url, ov.purace_ifg.bounds, { opacity: 0.75 });
            rasterOverlays.push(lPurace);
            overlayMaps["💥 " + ov.purace_ifg.title] = lPurace;
        }
        if (ov.purace_coh) {
            const lPuraceCoh = L.imageOverlay(ov.purace_coh.url, ov.purace_coh.bounds, { opacity: 0.80 });
            rasterOverlays.push(lPuraceCoh);
            overlayMaps["📶 " + ov.purace_coh.title] = lPuraceCoh;
        }
        if (ov.samanga_rgb) {
            const lRgbSam = L.imageOverlay(ov.samanga_rgb.url, ov.samanga_rgb.bounds, { opacity: 0.85 });
            rasterOverlays.push(lRgbSam);
            overlayMaps["📷 " + ov.samanga_rgb.title] = lRgbSam;
        }
        if (ov.samanga_ifg) {
            const lSamIfg = L.imageOverlay(ov.samanga_ifg.url, ov.samanga_ifg.bounds, { opacity: 0.75 });
            rasterOverlays.push(lSamIfg);
            overlayMaps["💥 " + ov.samanga_ifg.title] = lSamIfg;
        }
        if (ov.samanga_coh) {
            const lSamCoh = L.imageOverlay(ov.samanga_coh.url, ov.samanga_coh.bounds, { opacity: 0.80 });
            rasterOverlays.push(lSamCoh);
            overlayMaps["📶 " + ov.samanga_coh.title] = lSamCoh;
        }
        if (ov.samanga_ndvi) {
            const lNdvi = L.imageOverlay(ov.samanga_ndvi.url, ov.samanga_ndvi.bounds, { opacity: 0.78 });
            rasterOverlays.push(lNdvi);
            overlayMaps["🌿 " + ov.samanga_ndvi.title] = lNdvi;
        }
        if (ov.samanga_asi) {
            const lAsi = L.imageOverlay(ov.samanga_asi.url, ov.samanga_asi.bounds, { opacity: 0.78 });
            rasterOverlays.push(lAsi);
            overlayMaps["📡 " + ov.samanga_asi.title] = lAsi;
        }
        if (ov.sotara_sar) {
            const lSotara = L.imageOverlay(ov.sotara_sar.url, ov.sotara_sar.bounds, { opacity: 0.78 });
            rasterOverlays.push(lSotara);
            overlayMaps["⛰️ " + ov.sotara_sar.title] = lSotara;
        }
    }

    // Capas Oficiales de Amenaza Volcánica SGC (Polígonos Vectoriales de Zonificación)
    const amenazaPuraceGroup = L.layerGroup().addTo(sigMap);
    const amenazaSotaraGroup = L.layerGroup();

    if (typeof amenazaVolcanicaData !== 'undefined') {
        const renderThreatLayer = (geojsonData, targetGroup) => {
            if (!geojsonData || !geojsonData.features) return;
            L.geoJSON(geojsonData, {
                style: function(feature) {
                    const props = feature.properties || {};
                    const color = props.color || (props.nivel === 'Alta' ? '#ef4444' : (props.nivel === 'Media' ? '#f59e0b' : '#3b82f6'));
                    return {
                        color: color,
                        weight: props.nivel === 'Alta' ? 2.2 : 1.5,
                        opacity: 0.95,
                        fillColor: color,
                        fillOpacity: props.nivel === 'Alta' ? 0.28 : (props.nivel === 'Media' ? 0.20 : 0.14)
                    };
                },
                onEachFeature: function(feature, layer) {
                    const p = feature.properties || {};
                    layer.bindPopup(`
                        <div style="font-family: 'Inter', sans-serif; font-size: 0.84rem; line-height: 1.45; max-width: 280px;">
                            <strong style="color: ${p.color}; font-size: 0.95rem;">⚠️ ${p.volcan}</strong><br>
                            <span style="display: inline-block; padding: 2px 7px; border-radius: 4px; font-weight: 600; font-size: 0.75rem; background: ${p.color}25; color: ${p.color}; margin: 4px 0;">
                                Zonificación: ${p.amenaza_txt || p.nivel}
                            </span><br>
                            <strong>Fenómenos Peligrosos:</strong><br>
                            <span style="font-size: 0.78rem; color: #cbd5e1;">${p.fenomenos}</span><br>
                            ${p.area_km2 ? `<strong>Área Modelada:</strong> ${p.area_km2} km²<br>` : ''}
                            <span style="color: #94a3b8; font-size: 0.73rem;">Fuente Oficial: ${p.fuente}</span>
                        </div>
                    `);
                    layer.on('mouseover', function() {
                        this.setStyle({ fillOpacity: 0.45, weight: 3 });
                    });
                    layer.on('mouseout', function() {
                        this.setStyle({
                            fillOpacity: p.nivel === 'Alta' ? 0.28 : (p.nivel === 'Media' ? 0.20 : 0.14),
                            weight: p.nivel === 'Alta' ? 2.2 : 1.5
                        });
                    });
                }
            }).addTo(targetGroup);
        };

        if (amenazaVolcanicaData.purace) {
            renderThreatLayer(amenazaVolcanicaData.purace, amenazaPuraceGroup);
        }
        if (amenazaVolcanicaData.sotara) {
            renderThreatLayer(amenazaVolcanicaData.sotara, amenazaSotaraGroup);
        }
    }

    // Estaciones Geodésicas Continuas GeoRED SGC (Puntos de Verdad Terreno)
    gnssGroup = L.layerGroup().addTo(sigMap);
    if (typeof sgcGnssData !== 'undefined' && sgcGnssData.estaciones) {
        sgcGnssData.estaciones.forEach(st => {
            const isPop = st.id === 'POVA';
            const gnssMarker = L.circleMarker([st.lat, st.lon], {
                radius: isPop ? 9.5 : 8,
                fillColor: '#a855f7', // Violeta brillante
                color: '#ffffff',
                weight: 2.2,
                opacity: 1,
                fillOpacity: 0.95
            });

            gnssMarker.bindPopup(`
                <div style="font-family: 'Inter', sans-serif; font-size: 0.84rem; line-height: 1.45; max-width: 280px;">
                    <strong style="color: #a855f7; font-size: 0.95rem;">🛰️ Estación GNSS Continua [${st.id}]</strong><br>
                    <strong>Sitio:</strong> ${st.nombre}<br>
                    <strong>Municipio:</strong> ${st.municipio} (${st.departamento})<br>
                    <strong>Coordenadas:</strong> ${st.lat.toFixed(5)}°N, ${st.lon.toFixed(5)}°W<br>
                    ${st.altura_elipsoidal ? `<strong>Altura Elipsoidal:</strong> ${st.altura_elipsoidal} m<br>` : ''}
                    <div style="margin-top: 6px; padding: 4px 8px; background: rgba(168, 85, 247, 0.12); border-left: 3px solid #a855f7; border-radius: 4px;">
                        <strong>Rol en InSAR:</strong> <span style="color: #38bdf8; font-weight: 600;">${st.rol_insar}</span><br>
                        <span style="font-size: 0.75rem; color: #cbd5e1;">Anclaje geodésico milimétrico para validar velocidades LOS y vertical (V<sub>AA</sub>).</span>
                    </div>
                    <span style="color: #94a3b8; font-size: 0.73rem; display: block; margin-top: 4px;">Red: ${st.red}</span>
                </div>
            `);
            gnssGroup.addLayer(gnssMarker);
        });
    }

    // Grupos Vectoriales PS, SBAS, Referencias e Hitos
    const psGroup = L.layerGroup().addTo(sigMap);
    const sbasGroup = L.layerGroup().addTo(sigMap);
    const refGroup = L.layerGroup().addTo(sigMap);
    sgcGroup = L.layerGroup().addTo(sigMap);
    sgcMarkers = [];

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
                            <strong>ASI:</strong> ${st.ref_point.asi.toFixed(3)} (Fase de referencia = 0.0 mm)<br>
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
                        Lat: ${lm.lat.toFixed(4)}°N | Lon: ${lm.lon.toFixed(4)}°W<br>
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
                // Color por profundidad: Somero (<3km: Rojo), Intermedio (3-8km: Naranja), Profundo (>8km: Azul)
                const depthColor = attr.PROFUNDIDAD < 3.0 ? '#ef4444' : (attr.PROFUNDIDAD <= 8.0 ? '#f59e0b' : '#3b82f6');
                const sMarker = L.circleMarker([attr.LATITUD, attr.LONGITUD], {
                    radius: Math.max(7, attr.MAGNITUD * 5),
                    fillColor: depthColor,
                    color: '#ffffff',
                    weight: 1.5,
                    fillOpacity: 0.9
                });
                
                const distInfo = attr.VOLCAN_ASOCIADO && attr.VOLCAN_ASOCIADO.includes('Puracé') 
                    ? `A <strong>${attr.DIST_PURACE_KM} km</strong> del Cráter Puracé`
                    : `A <strong>${attr.DIST_SOTARA_KM} km</strong> del Complejo Sotará`;

                const precisionHtml = attr.GAP_DEG ? `
                    <div style="margin-top: 6px; padding: 4px 6px; background: rgba(255,255,255,0.05); border-radius: 4px; font-size: 0.76rem; color: #cbd5e1;">
                        <strong>Precisión Geofísica:</strong><br>
                        • Gap Azimutal: <strong>${attr.GAP_DEG}°</strong> | RMS: <strong>${attr.RMS_SEC} s</strong><br>
                        • Fases: ${attr.FASES}<br>
                        • Error Focal: H: ±${attr.ERR_H_KM} km | Z: ±${attr.ERR_Z_KM} km<br>
                        • Estaciones: <span style="color: #38bdf8;">${attr.ESTACIONES}</span>
                    </div>
                ` : '';

                sMarker.bindPopup(`
                    <div style="font-family: 'Inter', sans-serif; font-size: 0.84rem; line-height: 1.45; max-width: 285px;">
                        <strong style="color: ${depthColor}; font-size: 0.95rem;">🌋 ${attr.VOLCAN_ASOCIADO || 'Sismo SGC - OVSPop'}</strong><br>
                        <strong>Lugar:</strong> ${attr.LUGAR}<br>
                        <strong>Magnitud:</strong> ${attr.MAGNITUD.toFixed(1)} ML | <strong>Prof:</strong> ${attr.PROFUNDIDAD} km<br>
                        <strong>Foco:</strong> ${attr.CLASIFICACION_PROF || 'Volcánico'}<br>
                        <strong>Tipo:</strong> ${attr.TIPO || 'VT (Fracturamiento)'}<br>
                        <strong>Energía Liberada:</strong> ${attr.ENERGIA_TXT || '--'}<br>
                        <strong>Proximidad:</strong> ${distInfo}<br>
                        ${precisionHtml}
                        <span style="color: #94a3b8; font-size: 0.73rem;">Fecha UTC: ${attr.FECHA_UTC}</span>
                    </div>
                `);
                
                sgcGroup.addLayer(sMarker);
                sgcMarkers.push({
                    lat: attr.LATITUD,
                    lon: attr.LONGITUD,
                    layer: sMarker,
                    attr: attr
                });
            }
        });
    }

    // Controles de Capas
    overlayMaps["⚠️ Amenaza Puracé (SGC Oficial)"] = amenazaPuraceGroup;
    overlayMaps["⚠️ Amenaza Sotará (SGC Oficial)"] = amenazaSotaraGroup;
    overlayMaps["🛰️ Estaciones GNSS GeoRED (SGC)"] = gnssGroup;
    overlayMaps["🔵 Dispersores Persistentes (PS: ASI > 0.75)"] = psGroup;
    overlayMaps["🟡 Dispersores Distribuidos (SBAS: 0.60 - 0.75)"] = sbasGroup;
    overlayMaps["★ Puntos de Referencia (APS) e Hitos"] = refGroup;
    overlayMaps["🔴 Sismicidad SGC (OVSPop)"] = sgcGroup;

    L.control.layers(baseMaps, overlayMaps, { collapsed: false }).addTo(sigMap);
}

function filterSeismicity(filterType, btnElement) {
    currentSeismicFilter = filterType;

    // Actualizar botones de filtro
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    if (btnElement) {
        btnElement.classList.add('active');
    }

    // Re-renderizar lista
    renderSgcData(filterType);

    // Filtrar marcadores en el mapa Leaflet
    if (sgcMarkers && sgcMarkers.length > 0) {
        sgcMarkers.forEach(item => {
            const attr = item.attr;
            let match = false;
            if (filterType === 'ALL') {
                match = true;
            } else if (filterType === 'VT') {
                match = attr.TIPO && attr.TIPO.includes('VT');
            } else if (filterType === 'LP') {
                match = attr.TIPO && attr.TIPO.includes('LP');
            } else if (filterType === 'PURACE') {
                match = attr.VOLCAN_ASOCIADO && attr.VOLCAN_ASOCIADO.includes('Puracé');
            } else if (filterType === 'SOTARA') {
                match = attr.VOLCAN_ASOCIADO && attr.VOLCAN_ASOCIADO.includes('Sotará');
            }

            if (match) {
                if (!sgcGroup.hasLayer(item.layer)) {
                    sgcGroup.addLayer(item.layer);
                }
                item.layer.setStyle({ opacity: 1, fillOpacity: 0.9 });
            } else {
                if (sgcGroup.hasLayer(item.layer)) {
                    sgcGroup.removeLayer(item.layer);
                }
            }
        });
    }
}

function renderSgcData(filter = 'ALL') {
    const listContainer = document.getElementById('sgc-data-list');
    const statsContainer = document.getElementById('sgc-stats-container');

    if (typeof sgcData !== 'undefined' && sgcData && sgcData.length > 0) {
        // Cálculo de Estadísticas Sísmicas
        const totalCount = sgcData.length;
        let totalEnergyJoules = 0;
        let maxMag = 0;
        let shallowCount = 0;

        sgcData.forEach(ev => {
            const a = ev.attributes;
            totalEnergyJoules += (a.ENERGIA_JOULES || 0);
            if (a.MAGNITUD > maxMag) maxMag = a.MAGNITUD;
            if (a.PROFUNDIDAD < 3.0) shallowCount++;
        });

        const totalEnergyTxt = totalEnergyJoules >= 1e6 ? `${(totalEnergyJoules / 1e6).toFixed(1)} MJ` : `${(totalEnergyJoules / 1e3).toFixed(1)} kJ`;

        if (statsContainer) {
            statsContainer.innerHTML = `
                <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 3px 8px; border-radius: 6px; font-weight: 600;">⚡ Energía: ${totalEnergyTxt}</span>
                <span style="background: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 3px 8px; border-radius: 6px; font-weight: 600;">🔴 Someros (&lt;3km): ${shallowCount}</span>
                <span style="background: rgba(245, 158, 11, 0.15); color: #f59e0b; padding: 3px 8px; border-radius: 6px; font-weight: 600;">📈 Mag Máx: ${maxMag.toFixed(1)} ML</span>
            `;
        }

        // Conteo en botón Todos
        const countAllEl = document.getElementById('count-all');
        if (countAllEl) countAllEl.textContent = totalCount;

        // Filtrado de eventos
        const filteredEvents = sgcData.filter(event => {
            const a = event.attributes;
            if (filter === 'ALL') return true;
            if (filter === 'VT') return a.TIPO && a.TIPO.includes('VT');
            if (filter === 'LP') return a.TIPO && a.TIPO.includes('LP');
            if (filter === 'PURACE') return a.VOLCAN_ASOCIADO && a.VOLCAN_ASOCIADO.includes('Puracé');
            if (filter === 'SOTARA') return a.VOLCAN_ASOCIADO && a.VOLCAN_ASOCIADO.includes('Sotará');
            return true;
        });

        listContainer.innerHTML = '';
        if (filteredEvents.length === 0) {
            listContainer.innerHTML = '<div class="ticker-item"><span>No hay eventos sísmicos registrados para este filtro.</span></div>';
            return;
        }

        filteredEvents.forEach(event => {
            const attr = event.attributes;
            const item = document.createElement('div');
            item.className = 'ticker-item';

            const magColor = attr.MAGNITUD >= 1.8 ? 'var(--accent-red)' : 'var(--text-primary)';
            const profInfo = attr.PROFUNDIDAD ? ` | Prof: ${attr.PROFUNDIDAD} km` : '';
            const tipoInfo = attr.TIPO ? ` • ${attr.TIPO}` : '';
            const energiaBadge = attr.ENERGIA_TXT ? `<span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; margin-left: 6px;">⚡ ${attr.ENERGIA_TXT}</span>` : '';
            
            const telemetryBadge = attr.GAP_DEG ? `<span style="font-size: 0.72rem; color: #94a3b8; background: rgba(255,255,255,0.04); padding: 1px 5px; border-radius: 3px; margin-left: 6px;">Gap: ${attr.GAP_DEG}° | RMS: ${attr.RMS_SEC}s</span>` : '';

            item.innerHTML = `
                <div>
                    <span style="font-weight: 600; color: ${magColor}">${attr.LUGAR || 'Evento sísmico'}</span>
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">${tipoInfo}</span>
                    ${energiaBadge}
                    ${telemetryBadge}
                </div>
                <div style="display: flex; align-items: center; gap: 0.8rem;">
                    <span style="color: var(--text-secondary); font-size: 0.85rem;"><strong>${attr.MAGNITUD.toFixed(1)} ML</strong>${profInfo} — ${attr.FECHA_UTC}</span>
                    ${attr.LATITUD ? `<button class="map-btn" style="padding: 0.35rem 0.75rem; font-size: 0.78rem; font-weight: 600; cursor: pointer; background: var(--accent-blue); color: #0b0e14; border: none; border-radius: 6px;" onclick="flyToTarget(${attr.LATITUD}, ${attr.LONGITUD}, 14, this); return false;">📍 Ver en SIG</button>` : ''}
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
    renderSgcData('ALL');
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
