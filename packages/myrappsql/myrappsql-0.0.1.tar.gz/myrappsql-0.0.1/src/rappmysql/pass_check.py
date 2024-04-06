from werkzeug.security import generate_password_hash, check_password_hash
from cheltuieli.masina import Masina

class Users:
    def __init__(self, credentials):
        self.credentials = credentials

    @property
    def password(self):
        raise AttributeError('password is not readable attribute!!!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


if __name__ == '__main__':
    user = Users(None)
    print('Enter your password:')
    raw_password = input()
    # print('typed : _{}_'.format(raw_password))
    user.password = raw_password
    print('raw_password : _{}_'.format(user.password_hash))
    # test_password = input()
    # print(user.verify_password(test_password))
    app_masina = Masina()
    user.verify_password(app_masina.db_pass, user.password_hash)
