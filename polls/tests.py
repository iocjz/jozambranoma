from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service

class MySeleniumTests(LiveServerTestCase):
    # no crearem una BD de test en aquesta ocasió (comentem la línia)
    #fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.headless = True
        service = Service(GeckoDriverManager().install())
        cls.selenium = webdriver.Firefox(service=service, options=options)
        cls.selenium.implicitly_wait(5)

        # creem superusuari
        cls.user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        cls.user.is_staff = True
        cls.user.save()

        # Assignar permisos per veure usuaris
        permission = Permission.objects.get(codename='view_user')
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_user_permissions(self):
        # Iniciar sessió
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys("isard")
        password_input.send_keys("pirineus")
        password_input.send_keys(Keys.RETURN)

        # Comprovar que l'usuari pot veure la llista d'usuaris
        self.selenium.get(f"{self.live_server_url}/admin/auth/user/")
        self.assertIn("Users", self.selenium.title)

        # Comprovar que l'usuari no pot crear usuaris nous
        self.assertNotIn("Add user", self.selenium.page_source)

        # Comprovar que l'usuari no pot borrar usuaris
        self.assertNotIn("Delete selected", self.selenium.page_source)

