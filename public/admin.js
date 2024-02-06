document.addEventListener('DOMContentLoaded', function() {
    let loginFormId = document.getElementById('loginForm');
    let switchFormId = document.querySelector('.switch');

    let errorMessageShown = false;

    loginFormId.addEventListener('submit', function(event) {
        event.preventDefault();
        loginForm();
    });
    function showLoginErrorMessage(message) {
        if(errorMessageShown === true) return;
        let errorDiv = document.getElementById('invalid-username');
        errorDiv.style.display = 'block';
    }

    function loginForm() {
        let loginFormUsername = document.getElementById('login-username').value;
        let loginFormPassword = document.getElementById('login-password').value;
        if(loginFormUsername=="adminadmin"){

        if(loginFormUsername !== '' && loginFormPassword !== '') {
            fetch('/api/LoginUser', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: loginFormUsername, password: loginFormPassword}),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if(errorMessageShown) {
                            let errorDiv = document.getElementById('invalid-username');
                            errorDiv.style.display = 'none';
                        }
                        errorMessageShown = false;
                        window.location.href = 'adminpage.html';
                    } else {
                        showLoginErrorMessage(data.message);
                        errorMessageShown = true;
                    }
                })
                .catch(error => console.error(error));
        }}
        else{
            errorMessageShown=true;
        }
    }
});