#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest, os, requests, json
from cocoProject import create_test_app
from cocoProject.models import User, Coco, Routine
from config import Config


basedir = os.path.abspath(os.path.dirname(__file__))

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class CocoTestCase(unittest.TestCase):

    def setUp(self):
        self.app , self.db = create_test_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.db.create_all()
        

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        self.app_context.pop()

    def test_new_user(self):
        user = User(username='cocoproject',pw_hash='adfadf', dev_id='092809830skkdal')
        self.db.session.add(user)
        self.db.session.commit()
        self.assertIs(user, User.query.get_or_404(1))

    def test_new_coco(self):
        coco = Coco(name='coco', proxy='www.proxy.com', address='80:00:00:28', user_id=1,
                    cred='credentialsstr', timeConnection=datetime.utcnow(), deviceType='Coco')
        self.db.session.add(coco)
        self.db.session.commit()
        self.assertIs(coco, Coco.query.get_or_404(1))

    def test_new_routine(self):
        routine = Routine(task='Light', days='Monday, Tuesday', times='12,17', coco_id=1)
        self.db.session.add(routine)
        self.db.session.commit()
        self.assertIs(routine, Routine.query.get_or_404(1))


if __name__ == '__main__':
    unittest.main(verbosity=2)