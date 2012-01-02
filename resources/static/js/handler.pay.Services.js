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
				var $form, $field; 
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
