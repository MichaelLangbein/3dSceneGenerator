import proj4 from 'proj4';
import {register} from 'ol/proj/proj4';
import {get as getProjection, Projection} from 'ol/proj';


export function getViewParas(projection: string) {
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