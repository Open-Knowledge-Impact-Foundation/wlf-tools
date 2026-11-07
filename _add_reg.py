from requests import Session

sess = Session()
token = '' + 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzMDJjNjIzYTY4YTgyNWJlYWZiYTk1Y2VjZWM5NDY3YyIsImp0aSI6IjNmOTQ0OGQ1OGJmYzcyZWQ1Y2Y0YTRkNzIyYmMyMzc1Y2E4NTFhMWQyNzEwYzcwNTgzYjc0NTFlOGU5YWQxMWQ4ZDI2ZjA3Mzg0OWNmY2FlIiwiaWF0IjoxNjk1MjkwMTE2Ljc4MDA2OCwibmJmIjoxNjk1MjkwMTE2Ljc4MDA3MiwiZXhwIjozMzI1MjE5ODkxNi43NzU1Nywic3ViIjoiNTk2MDA5NjYiLCJpc3MiOiJodHRwczovL21ldGEud2lraW1lZGlhLm9yZyIsInJhdGVsaW1pdCI6eyJyZXF1ZXN0c19wZXJfdW5pdCI6NTAwMCwidW5pdCI6IkhPVVIifSwic2NvcGVzIjpbImJhc2ljIiwiaGlnaHZvbHVtZSIsImVkaXRwYWdlIiwiZWRpdHByb3RlY3RlZCIsImNyZWF0ZWVkaXRtb3ZlcGFnZSIsInVwbG9hZGZpbGUiLCJ1cGxvYWRlZGl0bW92ZWZpbGUiXX0.tiY03vOvDOKm9w0hzK0CKVNjgm64BNZUc8-6ZPG88fmlaUv8InvcbgVx0j2vwJr-9qDdTTwhaNc9VqaqT2sltgHAmNjCVgnVq_PksUx1LV_A9WmnrLNLF2E9q6t_IcmC3NEKeGPBGIGPCN4kc9zoZHfOhG2-VpXbp4loqTtGFr67lri7dvO0ckk6DiTolpMcOTzbLLkFYZQE-ZCCUtCoQBhsA9Vi5wojktSL1NWrnLAWtEFupxg7cyRrEAx6EyMNdJiNircM_yx4E4SKL71VrGtWj5QnpJFS435tXYjX5bJlylTuvd2gU-KRLeaj-XKrqj_ZgSKiTAsXGgul7QGVjOiNqNyHGiUta2wM-ZRV6ReUasOPq-aVd6bkYL5okdrhXL4z_BdfZJ-gyEdxCuoxxjkTDBpiyBwKWDspcFvAeiGjmr8wMs3hod805v-BY3WGjCk28OP4FrI-GhadELJ5Ciclz_PyD3o-muFkk-Qb12avHCNbUexacVGzGZ3LVJaJeuXXEtrtqnhjXeooFytTJIB0GFP9BjQW18Kk8MR3EgnEfDIcyOE3uvhPuUPq8-vYK25UUsHyQO6FHzd5E_qC9-euZSmDzL0uLse3Vx7BbduNcdEjyJChWcY4g_nAC55LPEHNZipbN3F5GGcmLx0QZ3fCgJd6wVamaKx1GsY0eVE'
sess.headers.update({'Authorization': 'Bearer ' + token})
def list_names(usernames):
    params = {
        'action': 'query',
        'list': 'users',
        'ususers': '|'.join(usernames),
        'usprop': 'registration',
        'format': 'json',
        'utf8': 1,
        'formatversion': 2,
        'uslimit': 'max'
    }
    return sess.get('https://en.wikipedia.org/w/api.php', params=params).json()['query']['users']
with open('no_registered_at.csv', 'r') as f:
    usernames = f.read().split('\n')
    sql = "UPDATE `user` SET `wiki_registered_at` = %s WHERE `username` = '%s'"
    for i in range(0, len(usernames), 25):
        usernames_ = list_names(usernames[i:i+25])
        with open('registered_at2.sql', 'a+') as f:
            for user in usernames_:
                f.write(sql % (f"\'{user['registration']}\'" if user.get('registration', None) else 'NULL', user['name']) + ';\n') 