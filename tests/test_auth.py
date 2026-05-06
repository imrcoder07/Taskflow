def test_login_success(client, member_user):
    response = client.post('/auth/login', data={
        'email': 'member@test.com',
        'password': 'Member123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign out' in response.data

def test_login_failure(client, member_user):
    response = client.post('/auth/login', data={
        'email': 'member@test.com',
        'password': 'WrongPassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_logout(client, member_user):
    client.post('/auth/login', data={
        'email': 'member@test.com',
        'password': 'Member123!'
    }, follow_redirects=True)
    
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign in to continue' in response.data
