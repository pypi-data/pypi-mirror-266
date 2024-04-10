

import 'jquery-validation';

import MyAMS from "./_utils";

const PyAMS_form = {

	init: (forms) => {

		$('label', forms).removeClass('col-md-3');
		$('.col-md-9', forms).removeClass('col-md-9');
		$('input, select, textarea', forms).addClass('form-control');
		$('button', forms).addClass('border');
		$('button[type="submit"]', forms).addClass('btn-primary');

		const lang = $('html').attr('lang');

		// Initialize select2 widgets

		const selects = $('.select2');
		if (selects.length > 0) {
			import("select2").then(() => {
				selects.each((idx, elt) => {
					const
						select = $(elt),
						data = select.data(),
						defaultOptions = {
							theme: data.amsSelect2Options || data.amsTheme || 'bootstrap4',
							language: data.amsSelect2Language || data.amsLanguage || lang
						},
						ajaxUrl = data.amsSelect2AjaxUrl || data.amsAjaxUrl || data['ajax-Url'];
					if (ajaxUrl) {
						// check AJAX data helper function
						let ajaxParamsHelper;
						const ajaxParams = MyAMS.getFunctionByName(
							data.amsSelect2AjaxParams || data.amsAjaxParams || data['ajax-Params']) ||
							data.amsSelect2AjaxParams || data.amsAjaxParams || data['ajax-Params'];
						if (typeof ajaxParams === 'function') {
							ajaxParamsHelper = ajaxParams;
						} else if (ajaxParams) {
							ajaxParamsHelper = (params) => {
								return _select2Helpers.select2AjaxParamsHelper(params, ajaxParams);
							}
						}
						defaultOptions.ajax = {
							url: MyAMS.getFunctionByName(
								data.amsSelect2AjaxUrl || data.amsAjaxUrl) ||
								data.amsSelect2AjaxUrl || data.amsAjaxUrl,
							data: ajaxParamsHelper || MyAMS.getFunctionByName(
								data.amsSelect2AjaxData || data.amsAjaxData) ||
								data.amsSelect2AjaxData || data.amsAjaxData,
							processResults: MyAMS.getFunctionByName(
								data.amsSelect2AjaxProcessResults || data.amsAjaxProcessResults) ||
								data.amsSelect2AjaxProcessResults || data.amsAjaxProcessResults,
							transport: MyAMS.getFunctionByName(
								data.amsSelect2AjaxTransport || data.amsAjaxTransport) ||
								data.amsSelect2AjaxTransport || data.amsAjaxTransport
						};
						defaultOptions.minimumInputLength = data.amsSelect2MinimumInputLength ||
							data.amsMinimumInputLength || data.minimumInputLength || 1;
					}
					const
						settings = $.extend({}, defaultOptions, data.amsSelect2Options || data.amsOptions || data.options),
						veto = {veto: false};
					select.trigger('before-init.ams.select2', [select, settings, veto]);
					if (veto.veto) {
						return;
					}
					const plugin = select.select2(settings);
					select.trigger('after-init.ams.select2', [select, plugin]);
				});
			});
		}

		// Initialize datetime widgets

		const dates = $('.datetime');
		if (dates.length > 0) {
			import("tempusdominus-bootstrap-4").then(() => {
				dates.each((idx, elt) => {
					const
						input = $(elt),
						data = input.data(),
						defaultOptions = {
							locale: data.amsDatetimeLanguage || data.amsLanguage || lang,
							icons: {
								time: 'far fa-clock',
								date: 'far fa-calendar',
								up: 'fas fa-arrow-up',
								down: 'fas fa-arrow-down',
								previous: 'fas fa-chevron-left',
								next: 'fas fa-chevron-right',
								today: 'far fa-calendar-check-o',
								clear: 'far fa-trash',
								close: 'far fa-times'
							},
							date: input.val(),
							format: data.amsDatetimeFormat || data.amsFormat
						},
						settings = $.extend({}, defaultOptions, data.datetimeOptions || data.options),
						veto = {veto: false};
					input.trigger('before-init.ams.datetime', [input, settings, veto]);
					if (veto.veto) {
						return;
					}
					input.datetimepicker(settings);
					const plugin = input.data('datetimepicker');
					if (data.amsDatetimeIsoTarget || data.amsIsoTarget) {
						input.on('change.datetimepicker', (evt) => {
							const
								source = $(evt.currentTarget),
								data = source.data(),
								target = $(data.amsDatetimeIsoTarget || data.amsIsoTarget);
							target.val(evt.date ? evt.date.toISOString(true) : null);
						});
					}
					input.trigger('after-init.ams.datetime', [input, plugin]);
				});
			});
		}

		// Initialize forms

		const defaultOptions = {
			submitHandler: PyAMS_form.submitHandler,
			messages: {}
		};

		const getFormOptions = (form, options) => {
			$('[data-ams-validate-messages]', form).each((idx, elt) => {
				options.messages[$(elt).attr('name')] = $(elt).data('ams-validate-messages');
				options.errorClass = 'error d-block';
				options.errorPlacement = (error, element) => {
					element.parents('div:first').append(error);
				};
			});
			return options;
		};

		const validateForms = () => {
			$(forms).each((idx, form) => {
				const options = $.extend({}, defaultOptions);
				$(form).validate(getFormOptions(form, options));
			});
		}

		if (lang === 'fr') {
			import("jquery-validation/dist/localization/messages_fr").then(() => {
				validateForms();
			});
		} else {
			validateForms();
		}
	},


	submitHandler: (form) => {

		const doSubmit = (form) => {
			const
				button = $('button[type="submit"]', form),
				name = button.attr('name'),
				input = $('input[name="' + name + '"]', form);
			if (input.length === 0) {
				$('<input />')
					.attr('type', 'hidden')
					.attr('name', name)
					.attr('value', button.attr('value'))
					.appendTo(form);
			}
			form.submit();
		};

		if (window.grecaptcha) {  // check if recaptcha was loaded
			const captcha_key = $(form).data('ams-form-captcha-key');
			grecaptcha.execute(captcha_key, {
				action: 'form_submit'
			}).then((token) => {
				$('.state-error', form).removeClass('state-error');
				$('input[name="g-recaptcha-response"]', form).val(token);
				doSubmit(form);
			});
		} else {
			doSubmit(form);
		}
	}

};


export default PyAMS_form;
