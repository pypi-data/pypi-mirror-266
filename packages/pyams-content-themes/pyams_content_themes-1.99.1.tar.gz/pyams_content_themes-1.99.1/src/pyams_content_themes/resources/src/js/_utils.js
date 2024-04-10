
const MyAMS = {

	/**
	 * Get target URL matching given source
	 *
	 * Given URL can include variable names (with their namespace), given between braces, as in {MyAMS.baseURL}
	 */
	getSource: (url) => {
		return url.replace(/{[^{}]*}/g, function (match) {
			return MyAMS.getFunctionByName(match.substr(1, match.length - 2));
		});
	},

	/**
	 * Get and execute a function given by name
	 * Small piece of code by Jason Bunting
	 */
	getFunctionByName: (functionName, context) => {
		if (typeof(functionName) === 'function') {
			return functionName;
		}
		if (!functionName) {
			return undefined;
		}
		const
			namespaces = functionName.split("."),
			func = namespaces.pop();
		context = (context === undefined || context === null) ? window : context;
		for (const namespace of namespaces) {
			try {
				context = context[namespace];
			} catch (e) {
				return undefined;
			}
		}
		try {
			return context[func];
		} catch (e) {
			return undefined;
		}
	},

	/**
	 * Get an object given by name
	 *
	 * @param objectName: dotted name
	 * @param context: original context, default to window
	 * @returns {Window|*|undefined}
	 */
	getObject: (objectName, context) => {
		if (typeof(objectName) !== 'string') {
			return objectName;
		}
		if (!objectName) {
			return undefined;
		}
		const namespaces = objectName.split(".");
		context = (context === undefined || context === null) ? window : context;
		for (const namespace of namespaces) {
			try {
				context = context[namespace];
			} catch (e) {
				return undefined;
			}
		}
		return context;
	},

	/**
	 * Script loader function
	 *
	 * @param url: script URL
	 * @param callback: a callback to be called after script loading
	 * @param options: a set of options to be added to AJAX call
	 * @param onerror: an error callback to be called instead of generic callback
	 */
	getScript: (url, callback, options, onerror) => {
		if (typeof(callback) === 'object') {
			onerror = options;
			options = callback;
			callback = null;
		}
		if (options === undefined) {
			options = {};
		}
		const
			defaults = {
				dataType: 'script',
				url: ams.getSource(url),
				success: callback,
				error: onerror || ams.error.show,
				cache: !ams.devmode,
				async: options.async === undefined ? typeof(callback) === 'function' : options.async
			};
		const settings = $.extend({}, defaults, options);
		return $.ajax(settings);
	},

	/**
	 * CSS file loader function
	 * Cross-browser code copied from Stoyan Stefanov blog to be able to
	 * call a callback when CSS is realy loaded.
	 * See: https://www.phpied.com/when-is-a-stylesheet-really-loaded
	 *
	 * @param url: CSS file URL
	 * @param id: a unique ID given to CSS file
	 * @param callback: optional callback function to be called when CSS file is loaded. If set, callback is called
	 *   with a 'first_load' boolean argument to indicate is CSS was already loaded (*false* value) or not (*true*
	 *   value).
	 * @param options: callback options
	 */
	getCSS: (url, id, callback, options) => {
		if (callback) {
			callback = MyAMS.getFunctionByName(callback);
		}
		const
			head = $('HEAD');
			style = $('style[data-ams-id="' + id + '"]', head);
		if (style.length === 0) {
			style = $('<style>').attr('data-ams-id', id)
				.text('@import "' + MyAMS.getSource(url) + '";');
			if (callback) {
				const styleInterval = setInterval(function () {
					try {
						const _check = style[0].sheet.cssRules;  // Is only populated when file is loaded
						clearInterval(styleInterval);
						callback.call(window, true, options);
					} catch (e) {
						// CSS is not loaded yet...
					}
				}, 10);
			}
			style.appendTo(head);
		} else {
			if (callback) {
				callback.call(window, false, options);
			}
		}
	},

	/**
	 * Initialize MyAMS data attributes
	 *
	 * @param element: source element
	 */
	initData: (element=document) => {
		$('[data-ams-data]', element).each((idx, elt) => {
			const
				dataElement = $(elt),
				data = dataElement.data('ams-data');
			if (data) {
				for (const name in data) {
					if (data.hasOwnProperty(name)) {
						let elementData = data[name];
						if (typeof (elementData) !== 'string') {
							elementData = JSON.stringify(elementData);
						}
						dataElement.attr('data-' + name, elementData);
					}
				}
			}
			dataElement.removeAttr('data-ams-data');
		});
	},

	/**
	 * MyAMS helpers
	 */
	helpers: {

		/**
		 * Click handler used to clear datetime input
		 */
		clearDatetimeValue: (evt) => {
			const
				target = $(evt.currentTarget).data('target'),
				picker = $(target).data('datetimepicker');
			if (picker) {
				picker.date(null);
			}
		}
	}
};


/**
 * Initialize custom click handlers
 */
$(document).on('click', '[data-ams-click-handler]', (event) => {
	const
		source = $(event.currentTarget),
		data = source.data();
	if (data.amsClickHandler) {
		if ((data.amsStopPropagation === true) || (data.amsClickStopPropagation === true)) {
			event.stopPropagation();
		}
		if (data.amsClickKeepDefault !== true) {
			event.preventDefault();
		}
		const handlers = data.amsClickHandler.split(/\s+/);
		for (const handler of handlers) {
			const callback = MyAMS.getFunctionByName(handler);
			if (callback !== undefined) {
				callback.call(source, event, data.amsClickHandlerOptions);
			}
		}
	}
});

/**
 * Initialize custom change handlers
 */
$(document).on('change', '[data-ams-change-handler]', (event) => {
	const source = $(event.target);
	// Disable change handlers for readonly inputs
	// These change handlers are activated by IE!!!
	if (source.prop('readonly')) {
		return;
	}
	const data = source.data();
	if (data.amsChangeHandler) {
		if ((data.amsStopPropagation === true) || (data.amsChangeStopPropagation === true)) {
			event.stopPropagation();
		}
		if (data.amsChangeKeepDefault !== true) {
			event.preventDefault();
		}
		const handlers = data.amsChangeHandler.split(/\s+/);
		for (const handler of handlers) {
			const callback = MyAMS.getFunctionByName(handler);
			if (callback !== undefined) {
				callback.call(source, event, data.amsChangeHandlerOptions);
			} else {
				console.debug(`Unknown change handler ${handler}!`);
			}
		}
	}
});

window.MyAMS = MyAMS;

export default MyAMS;
