// Google plus callback function
function signInCallback(authResult) {
    if (authResult['code']) {
        // Hide the sign-in button now that the user is authorized
        $('#signinButton').attr('style', 'display: none');
        // Send the one-time-use code to the server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main restaurants page
        $.ajax({
            type: 'POST',
            url: '/gconnect?state={{STATE}}',
            processData: false, // Do not process response into a string
            data: authResult['code'],
            contentType: 'application/octet-stream; charset=utf-8', // Send arbitrary binary stream of data using utf-8 encoding.
            success: function(result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    // If server resonds with success, show message and redirect to /restaurant after 4s
                    $('#result').html('Login Successful!</br>' + result + '</br>Redirecting...')
                    setTimeout(function() {
                        window.location.href = "/restaurant";
                    }, 4000);
                } else if (authResult['error']) {
                    console.log('There was an error: ' + authResult['error']);
                } else {
                    $('#result').html('Failed to make a server-side call. Check your configuration and console.');
                }
            }
        });
    }
}

// FB Callback Function
window.fbAsyncInit = function() {
    FB.init({
        appId: '1293669250698238',
        cookie: true, // enable cookies ot allow server to access the session
        xfbml: true, // parse social plugins on this page
        version: 'v2.8' // use version 2.8
    });
    FB.AppEvents.logPageView();
};
// Async load
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
        return;
    }
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function sendTokenToServer() {
    var access_token = FB.getAuthResponse()['accessToken']; // Retrieve access token
    console.log(access_token)
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
        console.log('Successful login for: ' + response.name);
        // make ajax call to server to send access token with state value
        $.ajax({
            type: 'POST',
            url: '/fbconnect?state={{STATE}}', // route is /fbconnect
            processData: false,
            data: access_token,
            contentType: 'application/octet-stream; charset=utf-8',
            success: function(result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    $('#result').html('Login Successful!</br>' + result + '</br>Redirecting...')
                    setTimeout(function() {
                        window.location.href = "/restaurant";
                    }, 4000);

                } else {
                    $('#result').html('Failed to make a server-side call. Check your configuration and console.');
                }
            }
        });
    });
}
