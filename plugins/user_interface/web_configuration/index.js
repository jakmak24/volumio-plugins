'use strict';

var libQ = require('kew');
var fs=require('fs-extra');
var config = new (require('v-conf'))();
var exec = require('child_process').exec;
var execSync = require('child_process').execSync;


module.exports = webConfiguration;
function webConfiguration(context) {
	var self = this;

	this.context = context;
	this.commandRouter = this.context.coreCommand;
	this.logger = this.context.logger;
	this.configManager = this.context.configManager;

}

webConfiguration.prototype.onVolumioStart = function()
{
	var self = this;
	var configFile=this.commandRouter.pluginManager.getConfigurationFile(this.context,'config.json');
	this.config = new (require('v-conf'))();
	this.config.loadFile(configFile);

    return libQ.resolve();
}

webConfiguration.prototype.onStart = function() {
    var self = this;
	var defer=libQ.defer();

    self.logger.info("PLUGIN_START");
		exec('python /data/plugins/user_interface/web_configuration/python_project/main.py')
	// Once the Plugin has successfull started resolve the promise
	defer.resolve();

    return defer.promise;
};

webConfiguration.prototype.onStop = function() {
    var self = this;
    var defer=libQ.defer();
		exec('pkill volumio_addon')
    // Once the Plugin has successfull stopped resolve the promise
    defer.resolve();

    return libQ.resolve();
};

webConfiguration.prototype.onRestart = function() {
    var self = this;
    // Optional, use if you need it
};


// Configuration Methods -----------------------------------------------------------------------------

webConfiguration.prototype.getUIConfig = function() {
    var defer = libQ.defer();
    var self = this;

    var lang_code = this.commandRouter.sharedVars.get('language_code');

    self.commandRouter.i18nJson(__dirname+'/i18n/strings_'+lang_code+'.json',
        __dirname+'/i18n/strings_en.json',
        __dirname + '/UIConfig.json')
        .then(function(uiconf)
        {
            uiconf.sections[0].content[0].value = self.config.get('sppobAddress.enabled');
            uiconf.sections[0].content[1].value.value = self.config.get('sppobAddress.group');
            uiconf.sections[0].content[1].value.label = self.config.get('sppobAddress.group').toString(16).toUpperCase();
            uiconf.sections[0].content[2].value.value = self.config.get('sppobAddress.device');
            uiconf.sections[0].content[2].value.label = self.config.get('sppobAddress.device').toString(16).toUpperCase();

            defer.resolve(uiconf);
        })
        .fail(function()
        {
            defer.reject(new Error());
        });

    return defer.promise;
};

webConfiguration.prototype.getConfigurationFiles = function()
{
	return ['config.json'];
}

webConfiguration.prototype.setUIConfig = function(data) {
	var self = this;
	//Perform your installation tasks here
};

webConfiguration.prototype.getConf = function(varName) {
	var self = this;
	//Perform your installation tasks here
};

webConfiguration.prototype.setConf = function(varName, varValue) {
	var self = this;
	//Perform your installation tasks here
};



// Playback Controls ---------------------------------------------------------------------------------------
// If your plugin is not a music_sevice don't use this part and delete it


webConfiguration.prototype.addToBrowseSources = function () {

	// Use this function to add your music service plugin to music sources
    //var data = {name: 'Spotify', uri: 'spotify',plugin_type:'music_service',plugin_name:'spop'};
    this.commandRouter.volumioAddToBrowseSources(data);
};

webConfiguration.prototype.handleBrowseUri = function (curUri) {
    var self = this;

    //self.commandRouter.logger.info(curUri);
    var response;


    return response;
};



// Define a method to clear, add, and play an array of tracks
webConfiguration.prototype.clearAddPlayTrack = function(track) {
	var self = this;
	self.commandRouter.pushConsoleMessage('[' + Date.now() + '] ' + 'webConfiguration::clearAddPlayTrack');

	self.commandRouter.logger.info(JSON.stringify(track));

	return self.sendSpopCommand('uplay', [track.uri]);
};

webConfiguration.prototype.seek = function (timepos) {
    this.commandRouter.pushConsoleMessage('[' + Date.now() + '] ' + 'webConfiguration::seek to ' + timepos);

    return this.sendSpopCommand('seek '+timepos, []);
};

// Stop
webConfiguration.prototype.stop = function() {
	var self = this;
	self.commandRouter.pushConsoleMessage('[' + Date.now() + '] ' + 'webConfiguration::stop');


};

// Spop pause
webConfiguration.prototype.pause = function() {
	var self = this;
	self.commandRouter.pushConsoleMessage('[' + Date.now() + '] ' + 'webConfiguration::pause');


};

// Get state
webConfiguration.prototype.getState = function() {
	var self = this;
	self.commandRouter.pushConsoleMessage('[' + Date.now() + '] ' + 'webConfiguration::getState');


};

//Parse state
webConfiguration.prototype.parseState = function(sState) {
	var self = this;
	self.commandRouter.pushConsoleMessage('[' + Date.now() + '] ' + 'webConfiguration::parseState');

	//Use this method to parse the state and eventually send it with the following function
};

// Announce updated State
webConfiguration.prototype.pushState = function(state) {
	var self = this;
	self.commandRouter.pushConsoleMessage('[' + Date.now() + '] ' + 'webConfiguration::pushState');

	return self.commandRouter.servicePushState(state, self.servicename);
};


webConfiguration.prototype.explodeUri = function(uri) {
	var self = this;
	var defer=libQ.defer();

	// Mandatory: retrieve all info for a given URI

	return defer.promise;
};

webConfiguration.prototype.getAlbumArt = function (data, path) {

	var artist, album;

	if (data != undefined && data.path != undefined) {
		path = data.path;
	}

	var web;

	if (data != undefined && data.artist != undefined) {
		artist = data.artist;
		if (data.album != undefined)
			album = data.album;
		else album = data.artist;

		web = '?web=' + nodetools.urlEncode(artist) + '/' + nodetools.urlEncode(album) + '/large'
	}

	var url = '/albumart';

	if (web != undefined)
		url = url + web;

	if (web != undefined && path != undefined)
		url = url + '&';
	else if (path != undefined)
		url = url + '?';

	if (path != undefined)
		url = url + 'path=' + nodetools.urlEncode(path);

	return url;
};

webConfiguration.prototype.search = function (query) {
	var self=this;
	var defer=libQ.defer();

	// Mandatory, search. You can divide the search in sections using following functions

	return defer.promise;
};

webConfiguration.prototype._searchArtists = function (results) {

};

webConfiguration.prototype._searchAlbums = function (results) {

};

webConfiguration.prototype._searchPlaylists = function (results) {

};

webConfiguration.prototype._searchTracks = function (results) {

};

webConfiguration.prototype.saveConfig = function(data)
{
    var self = this;
    self.config.set('sppobAddress.enabled',data['SppobEnabled']);
	self.config.set('sppobAddress.group',data['SppobGroup']['value']);
    self.config.set('sppobAddress.device',data['SppobDevice']['value']);
    exec('pkill -16 volumio_addon');
	self.commandRouter.pushToastMessage('success',"Sppob Address", "Configuration saved");
};
