"use strict";
(self["webpackChunkpyams_content_themes"] = self["webpackChunkpyams_content_themes"] || []).push([["src_pyams_content_themes_resources_src_js__form_js"],{

/***/ "./src/pyams_content_themes/resources/src/js/_form.js":
/*!************************************************************!*\
  !*** ./src/pyams_content_themes/resources/src/js/_form.js ***!
  \************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var jquery_validation__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! jquery-validation */ "./node_modules/jquery-validation/dist/jquery.validate.js");
/* harmony import */ var jquery_validation__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(jquery_validation__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./_utils */ "./src/pyams_content_themes/resources/src/js/_utils.js");
/* provided dependency */ var $ = __webpack_require__(/*! jquery */ "./node_modules/jquery/dist/jquery.js");


var PyAMS_form = {
  init: function init(forms) {
    $('label', forms).removeClass('col-md-3');
    $('.col-md-9', forms).removeClass('col-md-9');
    $('input, select, textarea', forms).addClass('form-control');
    $('button', forms).addClass('border');
    $('button[type="submit"]', forms).addClass('btn-primary');
    var lang = $('html').attr('lang');

    // Initialize select2 widgets

    var selects = $('.select2');
    if (selects.length > 0) {
      __webpack_require__.e(/*! import() */ "vendors-node_modules_select2_select2_js").then(__webpack_require__.t.bind(__webpack_require__, /*! select2 */ "./node_modules/select2/select2.js", 23)).then(function () {
        selects.each(function (idx, elt) {
          var select = $(elt),
            data = select.data(),
            defaultOptions = {
              theme: data.amsSelect2Options || data.amsTheme || 'bootstrap4',
              language: data.amsSelect2Language || data.amsLanguage || lang
            },
            ajaxUrl = data.amsSelect2AjaxUrl || data.amsAjaxUrl || data['ajax-Url'];
          if (ajaxUrl) {
            // check AJAX data helper function
            var ajaxParamsHelper;
            var ajaxParams = _utils__WEBPACK_IMPORTED_MODULE_1__["default"].getFunctionByName(data.amsSelect2AjaxParams || data.amsAjaxParams || data['ajax-Params']) || data.amsSelect2AjaxParams || data.amsAjaxParams || data['ajax-Params'];
            if (typeof ajaxParams === 'function') {
              ajaxParamsHelper = ajaxParams;
            } else if (ajaxParams) {
              ajaxParamsHelper = function ajaxParamsHelper(params) {
                return _select2Helpers.select2AjaxParamsHelper(params, ajaxParams);
              };
            }
            defaultOptions.ajax = {
              url: _utils__WEBPACK_IMPORTED_MODULE_1__["default"].getFunctionByName(data.amsSelect2AjaxUrl || data.amsAjaxUrl) || data.amsSelect2AjaxUrl || data.amsAjaxUrl,
              data: ajaxParamsHelper || _utils__WEBPACK_IMPORTED_MODULE_1__["default"].getFunctionByName(data.amsSelect2AjaxData || data.amsAjaxData) || data.amsSelect2AjaxData || data.amsAjaxData,
              processResults: _utils__WEBPACK_IMPORTED_MODULE_1__["default"].getFunctionByName(data.amsSelect2AjaxProcessResults || data.amsAjaxProcessResults) || data.amsSelect2AjaxProcessResults || data.amsAjaxProcessResults,
              transport: _utils__WEBPACK_IMPORTED_MODULE_1__["default"].getFunctionByName(data.amsSelect2AjaxTransport || data.amsAjaxTransport) || data.amsSelect2AjaxTransport || data.amsAjaxTransport
            };
            defaultOptions.minimumInputLength = data.amsSelect2MinimumInputLength || data.amsMinimumInputLength || data.minimumInputLength || 1;
          }
          var settings = $.extend({}, defaultOptions, data.amsSelect2Options || data.amsOptions || data.options),
            veto = {
              veto: false
            };
          select.trigger('before-init.ams.select2', [select, settings, veto]);
          if (veto.veto) {
            return;
          }
          var plugin = select.select2(settings);
          select.trigger('after-init.ams.select2', [select, plugin]);
        });
      });
    }

    // Initialize datetime widgets

    var dates = $('.datetime');
    if (dates.length > 0) {
      __webpack_require__.e(/*! import() */ "vendors-node_modules_tempusdominus-bootstrap-4_build_js_tempusdominus-bootstrap-4_js").then(__webpack_require__.t.bind(__webpack_require__, /*! tempusdominus-bootstrap-4 */ "./node_modules/tempusdominus-bootstrap-4/build/js/tempusdominus-bootstrap-4.js", 23)).then(function () {
        dates.each(function (idx, elt) {
          var input = $(elt),
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
            veto = {
              veto: false
            };
          input.trigger('before-init.ams.datetime', [input, settings, veto]);
          if (veto.veto) {
            return;
          }
          input.datetimepicker(settings);
          var plugin = input.data('datetimepicker');
          if (data.amsDatetimeIsoTarget || data.amsIsoTarget) {
            input.on('change.datetimepicker', function (evt) {
              var source = $(evt.currentTarget),
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

    var defaultOptions = {
      submitHandler: PyAMS_form.submitHandler,
      messages: {}
    };
    var getFormOptions = function getFormOptions(form, options) {
      $('[data-ams-validate-messages]', form).each(function (idx, elt) {
        options.messages[$(elt).attr('name')] = $(elt).data('ams-validate-messages');
        options.errorClass = 'error d-block';
        options.errorPlacement = function (error, element) {
          element.parents('div:first').append(error);
        };
      });
      return options;
    };
    var validateForms = function validateForms() {
      $(forms).each(function (idx, form) {
        var options = $.extend({}, defaultOptions);
        $(form).validate(getFormOptions(form, options));
      });
    };
    if (lang === 'fr') {
      __webpack_require__.e(/*! import() */ "node_modules_jquery-validation_dist_localization_messages_fr_js").then(__webpack_require__.t.bind(__webpack_require__, /*! jquery-validation/dist/localization/messages_fr */ "./node_modules/jquery-validation/dist/localization/messages_fr.js", 23)).then(function () {
        validateForms();
      });
    } else {
      validateForms();
    }
  },
  submitHandler: function submitHandler(form) {
    var doSubmit = function doSubmit(form) {
      var button = $('button[type="submit"]', form),
        name = button.attr('name'),
        input = $('input[name="' + name + '"]', form);
      if (input.length === 0) {
        $('<input />').attr('type', 'hidden').attr('name', name).attr('value', button.attr('value')).appendTo(form);
      }
      form.submit();
    };
    if (window.grecaptcha) {
      // check if recaptcha was loaded
      var captcha_key = $(form).data('ams-form-captcha-key');
      grecaptcha.execute(captcha_key, {
        action: 'form_submit'
      }).then(function (token) {
        $('.state-error', form).removeClass('state-error');
        $('input[name="g-recaptcha-response"]', form).val(token);
        doSubmit(form);
      });
    } else {
      doSubmit(form);
    }
  }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (PyAMS_form);

/***/ })

}]);
//# sourceMappingURL=src_pyams_content_themes_resources_src_js__form_js.js.map