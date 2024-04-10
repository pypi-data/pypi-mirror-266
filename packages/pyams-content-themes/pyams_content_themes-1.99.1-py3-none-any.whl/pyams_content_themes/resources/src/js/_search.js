

const PyAMS_search = {

	updateSort: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const index = $(evt.target).val();
			$('input[name="order_by"]', form).val(index);
			form.submit();
		}
	},

	updatePageLength: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const length = $(evt.target).val();
			$('input[name="start"]', form).val(0);
			$('input[name="length"]', form).val(length);
			form.submit();
		}
	},

	previousPage: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const current = $(evt.target).parents('.pagination').data('ams-current-page');
			const length = $('input[name="length"]', form).val();
			$('input[name="start"]', form).val(length * (current - 2));
			form.submit();
		}
	},

	nextPage: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const current = $(evt.target).parents('.pagination').data('ams-current-page');
			const length = $('input[name="length"]', form).val();
			$('input[name="start"]', form).val(length * current);
			form.submit();
		}
	},

	gotoPage: (evt) => {
		const form = $('form[id="search-results"]');
		if (form.length > 0) {
			const target = parseInt($(evt.target).text());
			const length = $('input[name="length"]', form).val();
			$('input[name="start"]', form).val(length * (target - 1));
			form.submit();
		}
	}
};


export default PyAMS_search;
