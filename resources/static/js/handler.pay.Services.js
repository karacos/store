/*
 * 
 */
define("store/handler.pay.Services",
	["jquery"],
	/**
	 * handler for services results
	 */
	function($) {
	return {
		'paypal_express': function(data) {
		},
		'paybox': function(data) {
			if (data.success) {
				var $form, $field, page, button, current_page; 
				if (typeof data.data === "object") {
					if (typeof data.data.target_url === "string") {
						$form = $('<form/>');
						$('body').empty().append('<h2>redirecting to payment page</h2>');
						$form.attr("method", "POST");
						$form.attr("action", data.data.target_url);
						$.each(data.data.params, function(k,v){
							$field = $('<input type="hidden"/>');
							$field.attr("name",k);
							$field.attr("value",v);
							$form.append($field);
						});
						$('body').append($form);
						$form.submit();
					}
				}
			} else {
				if (typeof data.message === "string") {
					page= $("#payment_result_message");
					if (page.length === 0) {
						page = $('<div id="payment_result_message" data-role="page"><div data-role="content"></div></div>')
						$('body').append(page);
					}
					button = $('<button>Retour</button>');
					current_page = $.mobile.activePage;
					button.click(function(){
						current_page.find('[kc-action]').button("enable");
						$.mobile.changePage(current_page);
					});
					page.find('[data-role="content"]').empty()
						.append(data.message)
						.append(button);
					button.buttonMarkup();
					$.mobile.changePage(page);
				}
				if (typeof data.data === "object") {
					if (typeof data.data.errurl === "string") {
						document.location = data.data.errurl;
						return;
					} else {
					}
				} else {
				}
			}
		}
	}
});
