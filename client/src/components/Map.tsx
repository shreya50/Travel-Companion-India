'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface POI {
  pageid: number;
  title: string;
  latitude: number;
  longitude: number;
  summary?: string;
  image_url?: string;
}

interface MapProps {
  center: [number, number];
  pois: POI[];
}

export default function Map({ center, pois }: MapProps) {
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Initialize Leaflet Map
    const map = L.map(mapRef.current, {
      center: center,
      zoom: 13,
      zoomControl: true,
      fadeAnimation: true
    });

    // Add CartoDB Dark Matter tile layer (sleek dark mode design match)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 20
    }).addTo(map);

    // Custom pulsing SVG/Tailwind indicator for markers (completely bypasses missing default image issues in bundlers)
    const customIcon = L.divIcon({
      html: `
        <div class="relative flex items-center justify-center w-6 h-6">
          <span class="absolute inline-flex h-6 w-6 animate-ping rounded-full bg-indigo-400/60 opacity-75"></span>
          <span class="relative inline-flex h-3.5 w-3.5 rounded-full bg-indigo-500 border-2 border-slate-100 shadow-md"></span>
        </div>
      `,
      className: 'custom-poi-marker',
      iconSize: [24, 24],
      iconAnchor: [12, 12],
      popupAnchor: [0, -10]
    });

    const markersGroup = L.featureGroup();

    pois.forEach((poi) => {
      const summaryText = poi.summary 
        ? (poi.summary.length > 120 ? poi.summary.substring(0, 120) + "..." : poi.summary)
        : "No description available.";

      const imageHtml = poi.image_url 
        ? `<img class="w-full h-24 object-cover rounded-md mb-2 border border-slate-700/50" src="${poi.image_url}" alt="${poi.title}" />` 
        : '';

      const popupContent = `
        <div class="p-1 max-w-[200px] text-slate-100">
          ${imageHtml}
          <h4 class="font-bold text-slate-100 text-xs mb-1 leading-snug">${poi.title}</h4>
          <p class="text-slate-400 text-[10px] leading-relaxed mb-3">${summaryText}</p>
          <a class="inline-flex w-full justify-center items-center px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-semibold rounded-md transition-colors text-center" href="/article/${poi.pageid}">
            Read Full Article &rarr;
          </a>
        </div>
      `;

      const marker = L.marker([poi.latitude, poi.longitude], { icon: customIcon })
        .bindPopup(popupContent);
      
      markersGroup.addLayer(marker);
    });

    markersGroup.addTo(map);

    // Auto-fit map viewport to include all markers
    if (pois.length > 0) {
      map.fitBounds(markersGroup.getBounds(), { padding: [40, 40] });
    }

    return () => {
      map.remove();
    };
  }, [center, pois]);

  return (
    <div className="w-full h-full relative rounded-2xl overflow-hidden border border-slate-800 shadow-xl bg-slate-900">
      <div ref={mapRef} className="w-full h-full min-h-[400px] md:min-h-0" />
    </div>
  );
}
