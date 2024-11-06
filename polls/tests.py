from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class MySeleniumTests(StaticLiveServerTestCase):
    # carregar una BD de test
    #fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)

        # creem superusuari
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = False
        user.is_staff = True
        user.save()
        # Assignar permisos per veure usuaris
        permission = Permission.objects.get(codename='view_user')
        user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_user_permissions(self):
        # anem directament a la pàgina d'accés a l'admin panel
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))

        # Iniciar sessió
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys("isard")
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys("pirineus")
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()

        # Comprovar que l'usuari pot veure la llista d'usuaris
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/auth/user/'))
        self.assertIn("Select user to view | Django site admin", self.selenium.title)

        # Comprovar que l'usuari no pot crear usuaris nous
        try:
            self.selenium.find_element(By.XPATH,'//a[@href="/admin/auth/user/add/"]')
            assert False, "Trobat element 'Add users' que NO hi ha de ser"
        except NoSuchElementException:
            pass

        # Comprovar que l'usuari no pot borrar usuaris
        try:
            self.selenium.find_element(By.XPATH,'//option[@value="delete_selected"]')
            assert False, "Trobat element 'Delete selected users' que NO hi ha de ser"
        except NoSuchElementException:
            pass
