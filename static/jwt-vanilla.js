const getCookie = (token) => {
    try {
        let cookieList = document.cookie.split(';');
        const cookieObjects = cookieList.map(cookie => {
        let key = cookie.split('=')[0].trim();
        let value = cookie.split('=')[1].trim();
        newObject = {};
        newObject[key] = value;
        return newObject
        })
        const tokenObject = cookieObjects.filter(cookieObject => Object.keys(cookieObject)[0] === token)
        return tokenObject[0][token]
    } catch (error) { error => {
        return `HTTP ${error.status} ${error.statusText}: ${error.json().msg}`
    }}
        
 }

const getToken = async () => {
    const email = document.getElementById('inputEmail')
    // const userElement = document.getElementById('username');
    const passwordElement = document.getElementById('inputPassword');
    const data = {
        email: email.value,
        // username: userElement.value,
        password: passwordElement.value

    };
    try {
        let request = await fetch("http://127.0.0.1:5000/signin", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            body: JSON.stringify(data)
        });
        response = await request.json();
        if (request.status != 200) {
            console.log(response)
        } else {
            const {current_user} = response;
            // await login(access_token);
            console.log(current_user);
            window.location.href= `http://127.0.0.1:5500/home/${current_user}`
            

            // await fetch("http://127.0.0.1:5500/home", {
            // method: 'POST',
            // credentials: 'include',
            // headers: {
            //     'Authorization': `Bearer ${access_token}`,
            //     'Content-Type': 'text/html; charset=utf-8'    
            // }}).then(response => {
            //     // console.log(response.text());
            //     return response.url
            // }).then(url => {
            //     window.location.href=
            // })
        
            // setTimeout(window.location.href = "http://127.0.0.1:5500/home/user",100)
        }
        
    } catch (err) {
        console.log('Errrrrorrrrr:', err)
    }
}

const getResource = async (url, elementID) => {
    try {
        const result = document.getElementById(elementID);
        let response = await fetch(url);
        if ( response.status === 401) {
            let request = await fetch('http://127.0.0.1:5000/token/refresh', {
                method: 'POST',
                headers: {
                    'X-CSRF-TOKEN': getCookie('csrf_refresh_token')
                },
                credentials: 'include'
            });
            if (request.status === 200) {
                let data = await request.json();
                getResource(url, elementID)
            }
        } else {
            let data = await response.json();
            result.textContent = JSON.stringify(data)  
        }
    } catch (error) {
        error => `HTTP ${error.status} ${error.statusText}: ${error.json().msg}`
    }   
}

// const logoutButton = document.getElementById("logout")
// logoutButton.addEventListener("click", logout)

const logout = async () => {
    try {
        const response = await fetch('http://127.0.0.1:5000/token/remove', {
            redirect: 'follow'
        })
        if (response.redirected) {
            window.location.href = response.url
            console.log(response)
            return response
        }
        
    } catch (error) {
        error => `Error ${error.status}: ${error.textContent}` 
    }   
}



