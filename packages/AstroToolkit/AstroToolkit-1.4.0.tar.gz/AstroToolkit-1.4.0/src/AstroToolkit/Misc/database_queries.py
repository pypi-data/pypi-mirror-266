from ..Misc.ProperMotionCorrection import get_adapted_radius
from ..Tools import query

import webbrowser

def query(type,pos,source,radius):
    if pos!=None:
        ra,dec=pos[0],pos[1]
    elif source!=None:
        gaia_data=query(type='data',survey='gaia',source=source)['data']
        ra,dec,pmra,pmdec=gaia_data['ra'][0],gaia_data['dec'][0],gaia_data['pmra'][0],gaia_data['pmdec'][0]
		
        # Scale search radius to include ~26 years of potential proper motion (doesn't actually correct coordinates, just gives a buffer)
        if type=='simbad':
            radius=get_adapted_radius([2016,0],[1990,0],pmra,pmdec,radius)
        elif type=='vizier':
            radius=get_adapted_radius([2016,0],[1990,0],pmra,pmdec,radius)

    if type=='simbad':
        if pos!=None:
            url=f'https://simbad.cds.unistra.fr/simbad/sim-coo?Coord={ra}+{dec}&CooFrame=FK5&CooEpoch=2000&CooEqui=2000&CooDefinedFrames=none&Radius={radius}&Radius.unit=arcsec&submit=submit+query&CoordList='
        elif source!=None:
            url=f'https://simbad.cds.unistra.fr/simbad/sim-coo?Coord={ra}+{dec}&CooFrame=FK5&CooEpoch=2000&CooEqui=2000&CooDefinedFrames=none&Radius={radius}&Radius.unit=arcsec&submit=submit+query&CoordList='
    elif type=='vizier':
        if dec>=0:
            url=f'https://vizier.cds.unistra.fr/viz-bin/VizieR-4?-c={ra}+{dec}&-c.rs={radius}&-out.add=_r&-sort=_r&-out.max=$4'
        else:
            url=f'https://vizier.cds.unistra.fr/viz-bin/VizieR-4?-c={ra}{dec}&-c.rs={radius}&-out.add=_r&-sort=_r&-out.max=$4'

    webbrowser.open_new_tab(url)

    return None