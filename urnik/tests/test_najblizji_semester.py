from django.test import TestCase
from urnik.models import Semester
from datetime import datetime


class TestNajblizjiSemester(TestCase):

    def test_prazno(self):
        datum = datetime(2020, 1, 1)
        self.assertRaises(Semester.DoesNotExist, Semester.najblizji_semester,
                          datum)

    def test_najblizji(self):
        sem1 = Semester.objects.create(
            od="2020-01-01", do="2020-10-01", ime="Semester 1", objavljen=True
        )
        blizu = Semester.najblizji_semester(datetime(2020, 9, 1))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2020, 10, 2))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2019, 10, 2))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2020, 11, 2))
        self.assertEqual(sem1, blizu)

        sem2 = Semester.objects.create(
            od="2020-10-05", do="2020-10-25", ime="Semester 2"
        )

        blizu = Semester.najblizji_semester(datetime(2020, 9, 1))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2020, 10, 2))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2019, 10, 2))
        self.assertEqual(sem1, blizu)

        blizu = Semester.najblizji_semester(datetime(2020, 10, 4))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2020, 11, 2))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2021, 11, 2))
        self.assertEqual(sem1, blizu)

        sem2.objavljen = True
        sem2.save()

        blizu = Semester.najblizji_semester(datetime(2020, 9, 1))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2020, 10, 2))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2019, 10, 2))
        self.assertEqual(sem1, blizu)
        blizu = Semester.najblizji_semester(datetime(2020, 10, 4))
        self.assertEqual(sem2, blizu)
        blizu = Semester.najblizji_semester(datetime(2020, 11, 2))
        self.assertEqual(sem2, blizu)
        blizu = Semester.najblizji_semester(datetime(2021, 11, 2))
        self.assertEqual(sem2, blizu)
