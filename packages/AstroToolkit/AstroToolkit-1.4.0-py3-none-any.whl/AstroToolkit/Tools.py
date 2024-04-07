'''
Changelog:
- added a webquery tool to perform SIMBAD/Vizier searches (matches functionality of datapage buttons)
- updated README to reflect new functionality
- Combined all query tools into a single tool 'query' which takes a 'type' argument.
- Combined all plotting tools into a single tool 'plot' which automatically tries to find the data type, or takes an argument 'type' as an override.
	- These two changes massively decrease the number of imports needed, and are now the main functions around which the whole toolkit works.
- Updated hrd plotting to fit the query/plot tools
- Updated datapage_creation example for new functionality
'''

'''
To-Do:
HIGH PRIORITY
- Better scaling for detection overlay sizes
- check config for if all keys are present, if not then make a new config file with existing key:value pairs saved
- talk to boris about combining lightcurves
- update README to reflect new changes (plots stored as dictionaries, showplot/saveplot/export now required to use on ATK plot objects, updated grid functionality)
  
MEDIUM PRIORITY
- add defaults for newly supported surveys to metadata table
- comment new code
- clean up / optimize anything that needs it to make development easier
- make some sort of error logging system that notes any errors encountered during runtime, maybe via a log file of some sort (?)

LOW PRIORITY
- (WEBSITE STILL DOWN?) update ASASA-SN SkyPatrol to v2 (don't like having to github clone it to install, still in beta)
- sort out lightcurve times, i.e. could in theory combine mjd/hjd lightcurves currently (not properly) --> starts to get into combining lightcurves across time domain (Boris spoke about this)
- add setting to config to change default hierarchy in 'any' survey searches (currently images/lightcurves)
'''

# Imports -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from bokeh.plotting import output_file
import re

from .Misc.file_naming import name_file
from .Misc.input_validation import validateinput

from importlib_resources import files
import configparser
import os

newline='\n'

# Configuration -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

config_file=files('AstroToolkit.Settings').joinpath('config.ini')	

# Create default config file if the file doesn't already exist (i.e. when the package is first installed)
# This handles all default parameters unless they are passed to a tool by the user, in which case these are overwritten
if not os.path.isfile(config_file):
	config=configparser.ConfigParser()

	config.add_section('settings')
	config.set('settings','enable_notifications','True')
	config.set('settings','dataquery_radius','3')
	config.set('settings','photquery_radius','3')
	config.set('settings','bulkphotquery_radius','3')
	config.set('settings','imagequery_size','30')
	config.set('settings','imagequery_overlays','gaia')
	config.set('settings','lightcurvequery_radius','3')
	config.set('settings','atlas_username','None')
	config.set('settings','atlas_password','None')
	config.set('settings','sed_radius','3')
	config.set('settings','spectrum_radius','3')
	config.set('settings','grid_size','250')
	config.set('settings','button_simbad_radius','3')
	config.set('settings','button_vizier_radius','3')
	config.set('settings','plot_size','400')
	config.set('settings','readfits_sourcename','source_id')
	config.set('settings','readfits_coordnames','ra,dec')

	with open(config_file,'w') as configfile:
		config.write(configfile)

# allows user to edit the config file
def editconfig(options):
	edit=configparser.ConfigParser()
	edit.read(config_file)
	settings=edit['settings']		

	accepted_keys=list(settings.keys())

	for key in options:
		if key not in accepted_keys:
			raise Exception(f'Invalid configuration parameter. Accepted parameters are {accepted_keys}.')
	
		settings[key]=str(options[key])
		
	with open(config_file,'w') as configfile:
		edit.write(configfile)
	
# Read config file
def readconfig():
	Config=configparser.ConfigParser()
	Config.read(config_file)

	settings=Config['settings']
	for key in settings:
		if settings[key]=='True':
			settings[key]='1'
		elif settings[key]=='False':
			settings[key]='0'

	config={}		

	# set up dictionary with key:value pairs of the config file
	config['ENABLE_NOTIFICATIONS']=int(settings['enable_notifications'])
	config['DATAQUERY_RADIUS']=float(settings['dataquery_radius'])
	config['PHOTQUERY_RADIUS']=float(settings['photquery_radius'])
	config['BULKPHOTQUERY_RADIUS']=float(settings['bulkphotquery_radius'])
	config['IMAGEQUERY_SIZE']=float(settings['imagequery_size'])
	config['IMAGEQUERY_OVERLAYS']=str(settings['imagequery_overlays'])
	config['LIGHTCURVEQUERY_RADIUS']=float(settings['lightcurvequery_radius'])
	config['ATLAS_USERNAME']=str(settings['atlas_username'])
	config['ATLAS_PASSWORD']=str(settings['atlas_password'])
	config['SED_RADIUS']=float(settings['sed_radius'])
	config['SPECTRUM_RADIUS']=float(settings['spectrum_radius'])
	config['GRID_SIZE']=int(settings['grid_size'])
	config['SIMBAD_RADIUS']=int(settings['button_simbad_radius'])
	config['VIZIER_RADIUS']=int(settings['button_vizier_radius'])
	config['PLOT_SIZE']=int(settings['plot_size'])
	config['READFITS_SOURCENAME']=str(settings['readfits_sourcename'])
	config['READFITS_COORDNAMES']=str(settings['readfits_coordnames']).split(',')
	
	return config

# prints the current value of a given config parameter to the terminal, and returns it
def getconfigvalue(parameter):
	config=readconfig()

	# make parameters returned by readconfig lower case to match the config file
	accepted_parameters=list(config.keys())
	for i,val in enumerate(accepted_parameters):
		accepted_parameters[i]=val.lower()

	if parameter not in accepted_parameters:
		raise Exception(f'{parameter} is not in accepted keys. Accepted keys: {accepted_parameters}')
	else:
		# get current value of parameter
		current_value=config[parameter.upper()]

		print(f'Current Value:{newline}{parameter} : {current_value}')
		return current_value

# Fetching ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def query(type,survey=None,source=None,pos=None,radius=None,size=None,overlays='default',band='g',sigmaclip=None,username=None,password=None,sources=None):
	config=readconfig()

	if survey==None and type not in ['sed','bulkphot','hrd']:
		raise Exception('argument "survey" required for given query type.')

	accepted_types=['data','phot','bulkphot','image','lightcurve','sed','spectra','reddening','hrd']
	if type not in accepted_types:
		raise Exception(f'Invalid type. Accepted types are {accepted_types}')

	if type in ['data','phot','bulkphot','image','lightcurve','sed','spectra']:
		if source!=None and pos!=None:
			raise Exception('Simultaneous pos and source input detected in query.')
		elif source==None and pos==None:
			raise Exception('pos or source input required for query.')
	elif type in ['reddening']:
		if source==None:
			raise Exception('Source input required for reddening query.')
	elif type in ['hrd']:
		if sources==None:
			raise Exception('Sources input required for hrd query.')

	if size!=None and type not in ['image']:
		print('Note: argument "size" does not affect given query type.')
	if overlays!='default' and type not in ['image']:
		print('Note: argument "overlays" does not affect given query type.')
	if band!='g' and type not in ['image']:
		print('Note: argument "band" does not affect given query type.')
	if sigmaclip!=None and type not in ['lightcurve']:
		print('Note: argument "sigma_clip" does not affect given query type.')
	if username!=None and type not in ['lightcurve']:
		print('Note: argument "username" does not affect given query type.')
	if password!=None and type not in ['lightcurve']:
		print('Note: argument "password" does not affect given query type.')

	if type=='data':
		# if a radius isn't supplied, use default value from config
		if radius==None:
			radius=config['DATAQUERY_RADIUS']

		# print notifications of currently running tools if enabled in the config
		if config['ENABLE_NOTIFICATIONS']==1:
			print(f'Running {survey} dataquery...{newline}source = {source}{newline}pos = {pos}{newline}radius = {radius}{newline}')

		from .Data.data import survey_map

		validateinput({'survey':survey,'pos':pos,'source':source,'radius':radius},'dataquery') 

		data=survey_map(survey=survey,pos=pos,source=source,radius=radius)

		return data
	

	elif type=='phot':
		if radius==None:
			radius=config['PHOTQUERY_RADIUS']

		# print notifications of current running tools if enabled in the config
		if config['ENABLE_NOTIFICATIONS']==1:
			print(f'Running {survey} photquery...{newline}source = {source}{newline}pos = {pos}{newline}radius = {radius}{newline}')

		from .Data.photometry import phot_query
		
		validateinput({'survey':survey,'pos':pos,'source':source,'radius':radius},'photquery')

		photometry=phot_query(survey=survey,pos=pos,source=source,radius=radius)

		return photometry
	

	elif type=='bulkphot':
		if radius==None:
			radius=config['BULKPHOTQUERY_RADIUS']

		# print notifications of currently running tools if enabled in the config
		if config['ENABLE_NOTIFICATIONS']==1:
			print(f'Running bulkphotquery...{newline}source = {source}{newline}pos = {pos}{newline}radius = {radius}{newline}')

		from .Data.photometry import bulk_query
		
		validateinput({'pos':pos,'source':source,'radius':radius},'bulkphot')

		data=bulk_query(pos=pos,source=source,radius=radius)
		
		return data
	

	elif type=='image':
		import numpy as np

		# get default size from config if one isn't supplied
		if size==None:
			size=config['IMAGEQUERY_SIZE']

		# get default overlay list from config if one isn't given
		if overlays=='default':
			overlays=config['IMAGEQUERY_OVERLAYS']
		
		if not isinstance(size,int):
			try:
				size=int(size)
			except:
				size_type=type(size)
				print(f'Invalid size data type. Expected int, got {size_type}.')

		# print notifications of currently running tools if enabled in the config
		if config['ENABLE_NOTIFICATIONS']==1:
			print(f'Running {survey} imagequery...{newline}source = {source}{newline}pos = {pos}{newline}size = {size}{newline}overlays = {overlays}{newline}')

		from .Data.imaging import image_correction
		
		validateinput({'survey':survey,'pos':pos,'source':source},'imagequery')

		# set all overlays to enabled
		if overlays=='all':
			overlays='gaia,galex_nuv,galex_fuv,rosat,sdss,twomass,wise,ztf,erosita,atlas,gaia_lc,asassn,crts'

		# split overlay string into a list, and check that they are all valid overlays.
		if overlays!=None:
			overlay_list=overlays.split(',')

			for i in range(0,len(overlay_list)):
				overlay_list[i]=overlay_list[i].lower()
			for i in range(0,len(overlay_list)):
				if overlay_list[i] not in ['gaia','galex_nuv','galex_fuv','rosat','ztf','wise','twomass','sdss','erosita','atlas','gaia_lc','asassn','crts']:
					raise Exception('invalid overlay')
		else:
			overlay_list=[]
		
		# validate some inputs based on the survey. E.g. each survey has a maximum size, and skymapper/panstarrs need to have their 'band' parameters formatted differently
		if survey=='panstarrs':
			if size>1500:
				raise Exception(f'Maximum supported size in {survey} is 1500 arcsec.')
			if not re.match('^[grizy]+$', band):
				raise Exception(f'Invalid {survey} bands. Supported bands are [g,r,i,z,y].')
		
		elif survey=='skymapper':
			if size>600:
				raise Exception(f'Maximum supported size in {survey} is 600 arcsec.')
			if re.match('^[grizuv]+$', band):
				pass
			else:
				raise Exception(f'Invalid {survey} bands. Supported bands are [g,r,i,z,u,v].')
		
			band=list(band)
			temp_string=''
			for i in range(0,len(band)):
				temp_string+=(band[i]+',')
			band=temp_string[:-1]
			
		elif survey=='dss':
			if band!='g':
				print('Note: DSS only supports g band imaging, input band has been ignored.')
			if size>7200:
				print(f'Maximum supported size in {survey} is 7200 arcsec.')

		# do hierarchical query
		if survey=='any':
			image=image_correction(survey='panstarrs',pos=pos,source=source,size=size,band=band,overlay=overlay_list)
			if image['data']==None:
				image=image_correction(survey='skymapper',pos=pos,source=source,size=size,band=band,overlay=overlay_list)
				if image['data']==None:
					image=image_correction(survey='dss',pos=pos,source=source,size=size,band=band,overlay=overlay_list)
					if image['data']==None:
						print('Note: No image found in any supported imaging survey.')
						pass
		
		# do single survey query
		else:
			image=image_correction(survey=survey,pos=pos,source=source,size=size,band=band,overlay=overlay_list)
		
		return image


	elif type=='lightcurve':
		from .Data.lightcurve_sigma_clip import sigma_clip

		# get radius from config if not given
		if radius==None:
			radius=config['LIGHTCURVEQUERY_RADIUS']
		
		# get username from config if not given (only used in ATLAS queries)
		if username==None:
			username=config['ATLAS_USERNAME']
		# get password from config if not given (only used in ATLAS queries)
		if password==None:
			password=config['ATLAS_PASSWORD']

		# enables notifications of currently running tools if enabled in config
		if config['ENABLE_NOTIFICATIONS']==1:
			print(f'Running {survey} lightcurvequery...{newline}source = {source}{newline}pos = {pos}{newline}radius = {radius}{newline}')

		from .Data.lightcurves import lightcurve_handling
		
		validateinput({'survey':survey,'pos':pos,'source':source,'radius':radius},'lightcurvequery')

		# if any data exists in any band, returns True. Otherwise, returns False
		def check_exists(data):
			data_exists=False
			for element in data:
				if element['data']!=None:
					data_exists=True
			
			return data_exists

		# uses above function to perform heirarchical query if asked for
		if survey=='any':
			data=query(type='lightcurve',survey='ztf',pos=pos,source=source,radius=radius)
			if check_exists(data)==False:
				data=query(type='lightcurve',survey='crts',pos=pos,source=source,radius=radius)
				if check_exists(data)==False:
					data=query(type='lightcurve',survey='atlas',pos=pos,source=source,radius=radius,username=username,password=password)
					if check_exists(data)==False:
						data=query(type='lightcurve',survey='asassn',pos=pos,source=source,radius=radius)
						if check_exists(data)==False:
							data=query(type='lightcurve',survey='gaia',pos=pos,source=source,radius=radius)

		# otherwise	perform single survey query
		else:
			data=lightcurve_handling(survey=survey,pos=pos,source=source,radius=radius,username=username,password=password)
		
		# performs sigma clip on data to given sigma level if wanted
		if sigmaclip!=None:
			clipped_data=[]
			for element in data:
				if element['data']!=None:
					clipped=sigma_clip(data=element,sigma=sigmaclip)
					clipped_data.append(clipped)
				else:
					clipped_data.append(None)

			data=clipped_data

		return data
	
	
	elif type=='sed':
		# sets radius from default in config if one isn't supplied
		if radius==None:
			radius=config['SED_RADIUS']	

		# enables notifications of currently running tools if enabled in the config
		if config['ENABLE_NOTIFICATIONS']==1:
			print(f'Running sedquery...{newline}source = {source}{newline}pos = {pos}{newline}radius = {radius}{newline}')	

		from .Data.sed import get_data
		
		data=get_data(pos=pos,source=source,radius=radius)
		
		validateinput({'source':source,'pos':pos},'sedquery')

		return data
	

	elif type=='spectra':
		# set radius to default in config if one isn't given
		if radius==None:
			radius=config['SPECTRUM_RADIUS']	

		# enables notifications of current running tool if enabled in config
		if config['ENABLE_NOTIFICATIONS']==1:
			print(f'Running {survey} spectrumquery...{newline}source = {source}{newline}pos = {pos}{newline}radius = {radius}{newline}')	

		from .Data.spectra import survey_map
		
		validateinput({'survey':survey,'pos':pos,'source':source,'radius':radius},'spectrumquery')

		data=survey_map(survey=survey,pos=pos,source=source,radius=radius)
		
		return data
	
	elif type=='reddening':
		from .Data.reddening import getreddening
	
		if source==None:
			raise Exception('getreddening requires source input.')

		validateinput({'source':source,'survey':survey},'reddeningquery')

		reddening=getreddening(source=source)
			
		return reddening
	
	elif type=='hrd':
		from .Plotting.HRD import get_data

		if source!=None and sources!=None:
			raise Exception('Simultaneous source and sources input detected in hrd query.')

		if isinstance(sources,list):
			for source in sources:
				validateinput({'source':source},'hrdquery')
		else:
			validateinput({'source':source})

		data=get_data(sources)

		return data
		

# Plotting ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def plot(data,type=None,colour='black',colours=None):
	config=readconfig()

	accepted_types=['image','lightcurve','sed','spectra','powspec','hrd']

	if colour!='black':
		print('Note: argument "colour" only has an effect in lightcurve plotting.')
	if colours!=None:
		print('Note: argument "colours" only has an effect in lightcurve plotting.')

	# if a type is not given, try to find the data type
	if type==None:
		# most data
		if isinstance(data,dict):
			try:
				found_type=data['type']
			except:
				raise Exception(f'No type given to plot(), and could not find a "type" key in given data. Accepted types are {accepted_types}' )
			
		# e.g. for lightcurves
		elif isinstance(data,list):
			try:
				# get type from first element. If multiple different types are found in the same list, raise an error.
				found_type=data[0]['type']
				for element in data:
					if element['type']!=found_type:
						raise Exception('Multiple data types found in given data. Only one type can be handled at a time.')
			except:
				raise Exception(f'No type given to plot(), and could not find a "type" key in given data. Accepted types are {accepted_types}' )
		
		type=found_type

	# if a type is given, it doesn't matter so much if a type is not found in the data, but still check and raise a warning if given type doesn't match the found type.
	elif type!=None:
		found_type=None	
		if isinstance(data,dict):
			try:
				found_type=data['type']
			except:
				pass
		elif isinstance(data,list):
			try:
				found_type=data[0]['type']
				for element in data:
					if element['type']!=found_type:
						raise Exception('Multiple data types found in given data. Only one type can be handled at a time.')
			except:
				pass

		if found_type!=None:
			if type!=found_type:
				print('Note: type found within given data does not match type passed by user.')


	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Plotting {type}...{newline}')
	

	if type=='image':
		from .Plotting.imaging import plot_image
	
		# plot image
		plot=plot_image(image_dict=data)

		# set file name
		if plot!=None:
			filename=name_file(data=data,data_type='ATKimage')
			output_file(filename)

			# scale plot size to values set by config
			plot.width,plot.height=config['PLOT_SIZE'],config['PLOT_SIZE']
		else:
			filename=None

		plot_dict={'type':data['type'],'survey':data['survey'],'source':data['source'],'pos':data['pos'],'plot':plot,'ATKfilename':filename}

		return plot_dict
	

	elif type=='lightcurve':
		from .Plotting.lightcurves import plot_lightcurve
	
		if colour not in ['green','red','blue','purple','orange','black']:
			raise Exception('Unsupported colour in plotlightcurve.')

		plot=plot_lightcurve(data=data,colour=colour,colours=colours)

		if plot!=None:
			# names file
			filename=name_file(data=data,data_type='ATKlightcurve')
			output_file(filename)
		
			# sets plot size according to config defaults
			plot.width,plot.height=config['PLOT_SIZE']*2,config['PLOT_SIZE']
		else:
			filename=None
		
		plot_dict={'type':'lightcurve'}

		if isinstance(data,list):
			for i,val in enumerate(data):
				if val!=None:
					plot_dict['survey']=val['survey']
					plot_dict['source']=val['source']
					plot_dict['pos']=val['pos']
		elif isinstance(data,dict):
			plot_dict['survey']=data['survey']
			plot_dict['source']=data['source']
			plot_dict['pos']=data['pos']
		else:
			raise Exception('Expected ATK lightcurve dict or list of ATK lightcurve dicts')

		plot_dict['plot']=plot
		plot_dict['ATKfilename']=filename

		return plot_dict
	
	
	elif type=='sed':
		from .Plotting.sed import plot_sed
	
		plot=plot_sed(sed_data=data)

		if plot!=None:
			# names file
			filename=name_file(data=data,data_type='ATKsed')
			output_file(filename)
		
			# scales plot according to defaults in the config
			plot.width,plot.height=config['PLOT_SIZE']*2,config['PLOT_SIZE']
		else:
			filename=None

		plot_dict={'type':data['type'],'source':data['source'],'pos':data['pos'],'plot':plot,'ATKfilename':filename}

		return plot_dict

	
	elif type=='spectra':
		from .Plotting.spectra import get_plot
	
		plot=get_plot(spectrum_dict=data)

		if plot!=None:
			# names file
			filename=name_file(data=data,data_type='ATKspectrum')
			output_file(filename)

			# sets plot sizes to defaults from config
			plot.width,plot.height=config['PLOT_SIZE']*2,config['PLOT_SIZE']
		else:
			filename=None

		plot_dict={'type':'spectra','survey':data['survey'],'source':data['source'],'pos':data['pos'],'plot':plot,'ATKfilename':filename}

		return plot_dict
	

	elif type=='powspec':
		import copy
		
		from .Plotting.powspec import get_plot
	
		# stops data from being flattened by the powspec plotting
		data_copy=copy.deepcopy(data)

		plot=get_plot(dataset=data_copy)

		if plot!=None:
			# name file
			filename=name_file(data=data,data_type='ATKpowspec')
			output_file(filename)
		
			# set size of file according to defaults in config
			plot.width,plot.height=config['PLOT_SIZE']*2,config['PLOT_SIZE']
		else:
			filename=None

		plot_dict={'type':'powspec'}
		for i,val in enumerate(data):
			if val!=None:
				plot_dict['survey']=val['survey']
				plot_dict['source']=val['source']
				plot_dict['pos']=val['pos']

		plot_dict['plot']=plot
		plot_dict['ATKfilename']=filename

		return plot_dict
	

	elif type=='hrd':
		from .Plotting.HRD import get_plot

		plot=get_plot(data)

		if plot!=None:
			# name file
			filename=name_file(data={'sources':data['sources']},data_type='ATKhrd')
			output_file(filename)

			# set plot size from config defaults
			plot.width,plot.height=config['PLOT_SIZE'],config['PLOT_SIZE']
		else:
			filename=None

		plot_dict={'sources':data['sources'],'type':'hrd','plot':plot,'ATKfilename':filename}
		
		return plot_dict

# Timeseries --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def tsanalysis(data):
	config=readconfig()

	# enables notifications of currently running tool if enabled in config
	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Running time series analysis...{newline}')	

	from .Timeseries.ztfanalysis import get_analysis
	
	# load timeseries analysis tool
	get_analysis(dataset=data)

# Data Pages --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def gridsetup(dimensions,plots,grid_size=None):
	config=readconfig()
	
	# sets the grid size to the default given in config if one isn't supplied
	if grid_size==None:
		grid_size=config['GRID_SIZE']

	# enables notifications of currently running tool if enabled in config
	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Creating grid...{newline}width = {dimensions["width"]}{newline}height = {dimensions["height"]}{newline}grid_size = {grid_size}{newline}')

	from .Datapages.grid import get_grid
	
	plots=get_grid(dimensions=dimensions,plots=plots,grid_size=grid_size)
	
	return plots

def getbuttons(grid_size=None,source=None,pos=None,simbad_radius=None,vizier_radius=None):
	config=readconfig()
	
	# gets default grid size from config if one isn't given
	if grid_size==None:
		grid_size=config['GRID_SIZE']
	# gets default radius to use in SIMBAD query for SIMBAD button if one isn't given
	if simbad_radius==None:
		simbad_radius=config['SIMBAD_RADIUS']
	# gets default radius to use in Vizier query for Vizier button if one isn't given
	if vizier_radius==None:
		vizier_radius=config['VIZIER_RADIUS']

	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Generating info buttons...{newline}source = {source}{newline}pos = {pos}{newline} simbad_radius = {simbad_radius}{newline}vizier_radius = {vizier_radius}{newline}')

	from .Datapages.buttons import getinfobuttons	

	validateinput({'source':source,'pos':pos},'databuttons')

	if source!=None and pos!=None:
		raise Exception('Simultaneous pos and source input detected in getbuttons.')
	elif source==None and pos==None:
		raise Exception('pos or source input required in getbuttons.')

	# validates data type of some parameters. Since these are only used here, didn't add to validateinput
	if not (isinstance(simbad_radius,int) or isinstance(simbad_radius,float)):
		data_type=type(simbad_radius)
		raise Exception(f'Incorrect simbad_radius data type. Expected float/int, got {data_type}.')
	if not (isinstance(vizier_radius,int) or isinstance(vizier_radius,float)):
		data_type=type(vizier_radius)
		raise Exception(f'Incorrect vizier_radius data type. Expected float/int, got {data_type}.')
	if not (isinstance(grid_size,int) or isinstance(grid_size,float)):
		data_type=type(grid_size)
		raise Exception(f'Incorrect grid_size data type. Expected float/int, got {data_type}.')

	# get buttons
	plot=getinfobuttons(grid_size=grid_size,source=source,pos=pos,simbad_radius=simbad_radius,vizier_radius=vizier_radius)
	
	plot_dict={'type':'buttons','source':source,'pos':pos,'plot':plot}

	return plot_dict

def getmdtable(metadata,pos=None,source=None):
	config=readconfig()

	# enables notifications of currently running tool if enabled in config
	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Generating metadata table...{newline}source = {source}{newline}pos = {pos}{newline}')	

	from .Datapages.metadata import gettable

	if source!=None and pos!=None:
		raise Exception('Simultaneous pos and source input detected in getmdtable.')
	elif source==None and pos==None:
		raise Exception('pos or source input required in getmdtable.')
	
	plot=gettable(metadata_dict=metadata,pos=pos,source=source)
	
	plot_dict={'type':'metadata','source':source,'pos':pos,'plot':plot}

	return plot_dict

# File Handling -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def savedata(data):
	config=readconfig()

	# enables notifications for currently running tool if enabled in config
	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Saving data to local storage...{newline}')	

	from .Misc.file_handling import create_file
	
	fname=create_file(data_copy=data)
	
	return fname
	
def readdata(filename):
	config=readconfig()

	# enables notifications for currently running tool if enabled in config
	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Reading data from local storage...{newline}')	

	from .Misc.file_handling import read_file
	
	if not isinstance(filename,str):
		data_type=type(filename)
		raise Exception(f'Incorrect filename datatype. Expected str, got {data_type}.')

	data=read_file(file_name=filename)
	
	return data

# These are taken from bokeh, it is just annoying to have to import separately from bokeh every time you want a plot
def showplot(plot):
	from bokeh.plotting import show

	try:
		if isinstance(plot,dict):
			figure=plot['plot']
		else:
			figure=plot
		show(figure)
	except:
		raise Exception('Unexpected data type passed to showplot, expected ATK plot dict or bokeh plot object')
	
def saveplot(plot):
	from bokeh.plotting import save

	try:
		if isinstance(plot,dict):
			figure=plot['plot']
		else:
			figure=plot
		save(figure)
	except:
		raise Exception('Unexpected data type passed to saveplot, expected ATK plot dict or bokeh plot object')
	
	fname=save(figure)

	print(f'Saved file to {fname}.')

	return fname

# exports plots to PNG. Have to use bokeh save() as a proxy to get the filename, so give an option to keep/delete the .html file.
def export(plot):
	config=readconfig()

	# enables notifications for currently running tool if enabled in config
	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Exporting plot to PNG...{newline}')

	from bokeh.io import export_png
	from bokeh.plotting import save

	if isinstance(plot,dict):
		try:
			filename=plot['ATKfilename']
			export_png(plot['plot'],filename=f'{filename[:-5]}.png')
		except:
			raise Exception("Unexpected structure of dict passed to export. Required keys: 'plot','ATKfilename'")
	else:
		try:
			# have to save plot as a proxy to get file name, could then rm this but this would potentially delete fils that were not meant to be deleted.
			filename=save(plot)
			export_png(plot,filename=f'{filename[:-5]}.png')
		except:
			raise Exception('Unexpected plot type, expected ATK dict or bokeh plot object.')

	return None

# Miscellaneous -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def webquery(type,pos=None,source=None,radius=None):
	from .Misc.database_queries import query

	config=readconfig()

	if type.lower() not in ['simbad','vizier']:
		raise Exception(f"Invalid webquery type '{type}'. Valid types: ['simbad','vizier']")

	# gets default radius to use in SIMBAD query if one isn't given
	if radius==None and type=='simbad':
		radius=config['SIMBAD_RADIUS']
	# gets default radius to use in Vizier query if one isn't given
	elif radius==None and type=='vizier':
		radius=config['VIZIER_RADIUS']

	if config['ENABLE_NOTIFICATIONS']==1:
		print(f'Performing {type} query...{newline}source = {source}{newline}pos = {pos}{newline} radius = {radius}{newline}')

	validateinput({'source':source,'pos':pos},'webquery')

	if source!=None and pos!=None:
		raise Exception('Simultaneous pos and source input detected in webquery.')
	elif source==None and pos==None:
		raise Exception('pos or source input required in webquery.')
	
	query(type=type,source=source,pos=pos,radius=radius)

def correctpm(inputtime,targettime,ra,dec,pmra,pmdec):
	from .Misc.ProperMotionCorrection import PMCorrection
	
	pos=PMCorrection(input=inputtime,target=targettime,ra=ra,dec=dec,pmra=pmra,pmdec=pmdec)

	return pos

def getdistance(parallax):
	# parallax must be in mas
	distance=1/(parallax*10**-3)
	return distance

def convfromdeg(pos):
	from .Misc.coord_conversion import convert_to_hmsdms

	pos=convert_to_hmsdms(pos)
	
	return pos

def convtodeg(pos):
	from .Misc.coord_conversion import convert_to_deg
	
	pos=convert_to_deg(pos)
	
	return pos

def getsources(file_name,col_name=None):
	from .Misc.read_fits import get_source_list
	
	# gets the default source column name from the config if one is not given
	if col_name==None:
		config=readconfig()
		parameter=config['READFITS_SOURCENAME']
	else:
		parameter=col_name

	sources=get_source_list(file_name,parameter)
	return sources

def getpositions(file_name,col_names=None):
	from .Misc.read_fits import get_pos_list

	# here, col_names are ra,dec. Gets these from the config if none are given.
	if col_names==None:
		config=readconfig()
		parameters=config['READFITS_COORDNAMES']
	else:
		parameters=col_names

	pos_list=get_pos_list(file_name,parameters)
	return pos_list

def getcolumn(file_name,col_name):
	from .Misc.read_fits import get_column

	values_list=get_column(file_name,col_name)
	return values_list

# used for installation process, as there is some manual stuff that needs to be done inside package directory
def getpath():
	path = os.path.dirname(__file__)
	print(path)