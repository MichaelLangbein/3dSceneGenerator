import './style.css'
import 'ol/ol.css';
import { Map, View } from 'ol';
import { Tile as TileLayer } from 'ol/layer';
import { OSM, GeoTIFF } from 'ol/source';
import { ScaleLine, Zoom, MousePosition, Attribution } from 'ol/control';
import cogUrl from '../data/s2/TCI.tif?url';




const container = document.getElementById('map') as HTMLDivElement;

const osmLayer = new TileLayer({
    source: new OSM()
})


const s2Layer = new TileLayer({
    source: new GeoTIFF({
        sources: [{
            url: cogUrl,
        }],
    })
})

const layers = [osmLayer, s2Layer];

const view = new View({
    // projection: 'EPSG:3857',
    // center: [1258439, 6123673],
    projection: 'EPSG:4326',
    center: [11.3, 48],
    zoom: 12,
});

const controls = [new ScaleLine(), new Zoom(), new MousePosition(), new Attribution()];

const map = new Map({
    target: container,
    layers: layers,
    view: view,
    controls: controls,
});