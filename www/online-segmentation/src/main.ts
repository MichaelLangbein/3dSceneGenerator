import './style.css'
import 'ol/ol.css';
import { Map, View } from 'ol';
import { Tile as TileLayer } from 'ol/layer';
import WebGLTileLayer from 'ol/layer/WebGLTile';
import { OSM, GeoTIFF } from 'ol/source';
import { ScaleLine, Zoom, MousePosition, Attribution } from 'ol/control';
import proj4 from 'proj4';
import {register} from 'ol/proj/proj4';
import {get as getProjection, Projection} from 'ol/proj';
import cogUrl from '../data/s2/TCI.tif?url';
// const cogUrl = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/32/U/PU/2022/6/S2B_32UPU_20220612_0_L2A/TCI.tif";



function getViewParas(projection: string) {
    switch (projection) {
        case 'EPSG:4326':
            return {
                projection: 'EPSG:4326',
                center: [11.3, 48],
                zoom: 12,
            };
        case 'EPSG:3857':
            return {
                projection: 'EPSG:3857',
                center: [1258439, 6123673],
                zoom: 12,
            };
        case 'EPSG:32632':
            proj4.defs('EPSG:32632', '+proj=utm +zone=32 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ');
            register(proj4);
            const projection = getProjection('EPSG:32632') as Projection;
            return {
                projection: projection,
                center: [670628, 5326397],
                zoom: 12,
            };
        default: 
            throw Error();
    }

}

const viewParameters = getViewParas('EPSG:4326');

const container = document.getElementById('map') as HTMLDivElement;

const osmLayer = new TileLayer({
    source: new OSM()
})


const s2Layer = new WebGLTileLayer({
    source: new GeoTIFF({
        sources: [{
            url: cogUrl,
        }],
    })
})

const layers = [osmLayer, s2Layer];

const view = new View(viewParameters);

const controls = [new ScaleLine(), new Zoom(), new MousePosition(), new Attribution()];

const map = new Map({
    target: container,
    layers: layers,
    view: view,
    controls: controls,
});