let inMemoryToken;

function login ({ jwt_token, jwt_token_expiry }, noRedirect) {
  inMemoryToken = {
    token: jwt_token,
    expiry: jwt_token_expiry
  };
  if (!noRedirect) {
    Router.push('/app')
  }
}


async function logout () {
    inMemoryToken = null;
    const url = '/api/logout'
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
    })
}