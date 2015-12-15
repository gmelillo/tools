vcl 4.0;

backend default {
	.host = "127.0.0.1";
	.port = "80";
	.connect_timeout = 60s;
	.first_byte_timeout = 60s;
	.between_bytes_timeout = 60s;
	.max_connections = 20;
}

sub vcl_recv {
	set req.backend_hint = default;
	
	# Disable cache on administrative pages
	if (req.url ~ "/wp-(login|admin|cron)") {
		return (pass);
	}
	# Disable cache on architetti lounge
	if (req.url ~ "/(architect-lounge|usermng|preferiti|logout)") {
		return (pass);
	}
	# Disable cache on login pages
	if (req.url ~ "preview=true") {
		return (pass);
	}
	# Disable cache if user is logged in
	if (req.http.Cookie && req.http.Cookie ~ "(wordpress_|wordpress_logged_in|comment_author_)") {
		return (pass);
	}
	# Don't cache ajax requests, urls with ?nocache or comments/login/regiser
	if(req.http.X-Requested-With == "XMLHttpRequest" || req.url ~ "nocache" || req.url ~ "(control.php|wp-comments-post.php|wp-login.php|register.php|xmlrpc.php)") {
		return (pass);
	}

	return (hash);
}

sub vcl_backend_response {
	if (beresp.ttl < 60s) {
		set beresp.ttl = 60s;
		unset beresp.http.Cache-Control;
	}
        return (deliver);
}