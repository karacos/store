define("store/handler.Store.pay_dummy_cart",
	["jquery",
	 "karacos/lib/handlers.registry",
	 "store/handler.pay.Services"
	], function($, handlersRegistry,service_handlers){
		var karacos, auth;
		$('body').bind('kcauth', function(){
			karacos = KaraCos;
			auth = karacos.authManager;
		});
		handlersRegistry.returnHandlers['pay_dummy_cart'] = function(data,$form, callback) {
			if (typeof data.data === "object") {
				if (typeof data.data.service === "string") {
					if (typeof service_handlers[data.data.service] === "function") {
						service_handlers[data.data.service](data);
					}
				}
			}
		};
		return handlersRegistry;
})