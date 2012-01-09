/**
 * This handler is usually unused, it stands as example for overriding
 */

define("store/handler.Store.validate_cart",
	["jquery",
	 "karacos/lib/handlers.registry"
	], function($, handlersRegistry){
		var karacos, auth;
		$('body').bind('kcauth', function(){
			karacos = KaraCos;
			auth = karacos.authManager;
		});
		handlersRegistry.returnHandlers['validate_cart'] = function(data,$form, callback) {
			callback(data);
		};
		return handlersRegistry;
})