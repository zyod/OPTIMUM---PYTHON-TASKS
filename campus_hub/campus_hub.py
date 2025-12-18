"""
Campus Resource Hub — OOP Capstone Project
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Iterable


# ======================= MIXIN =======================


class AuditMixin:
    """Logs monetary and resource actions."""

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[AUDIT {timestamp}] {message}")


# ======================= WALLET =======================


class Wallet(AuditMixin):
    def __init__(self, balance: float = 0.0):
        if balance < 0:
            raise ValueError("Initial balance must be >= 0")
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float):
        self._validate(amount)
        self._balance += amount
        self._log(f"Deposit +{amount:.2f}")

    def withdraw(self, amount: float):
        self._validate(amount)
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self._log(f"Withdraw -{amount:.2f}")

    def transfer(self, other: "Wallet", amount: float):
        self.withdraw(amount)
        other.deposit(amount)
        self._log(f"Transfer {amount:.2f}")

    @staticmethod
    def _validate(amount: float):
        if amount <= 0:
            raise ValueError("Amount must be positive")


# ======================= PERSON =======================


class Person(ABC):
    _id_counter = 1

    def __init__(self, name: str):
        if not name:
            raise ValueError("Name cannot be empty")
        self.name = name
        self.id = Person._id_counter
        Person._id_counter += 1
        self.wallet = Wallet()

    def __eq__(self, other):
        return isinstance(other, Person) and self.id == other.id

    @abstractmethod
    def role(self) -> str:
        pass


# ======================= COURSE =======================


class Course:
    max_students = 2

    def __init__(self, title: str):
        self.title = title
        self.current_students: List["Student"] = []

    def enroll(self, student: "Student"):
        if len(self.current_students) >= Course.max_students:
            raise ValueError("Course full")
        self.current_students.append(student)

    def __str__(self):
        return self.title


# ======================= RESOURCE =======================


class Resource:
    def __init__(self, rid: str, rtype: str):
        self.id = rid
        self.type = rtype
        self.available = True

    def __str__(self):
        status = "available" if self.available else "allocated"
        return f"Resource(id={self.id}, type={self.type}, status={status})"


# ======================= STUDENT =======================


class Student(Person):
    def __init__(self, name: str):
        super().__init__(name)
        self.courses: List[Course] = []
        self._progress = 0

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if not 0 <= value <= 100:
            raise ValueError("Progress must be 0–100")
        self._progress = value

    def enroll(self, course: Course, mentor=None):
        course.enroll(self)
        self.courses.append(course)
        print(f"Enrolled: {self.name} -> {course}")

    def needs_resource(self):
        return True

    def role(self):
        return "Student"


class PremiumStudent(Student):
    def enroll(self, course: Course, mentor):
        super().enroll(course)
        print(f"Mentor matched: {mentor.name}")

    def role(self):
        return "PremiumStudent"


# ======================= MENTOR =======================


class Mentor(Person):
    def __init__(self, name: str):
        super().__init__(name)
        self.approvals = 0

    def approve(self, resource: Resource, student: Student):
        if resource.available:
            resource.available = False
            self.approvals += 1
            print(
                f"Resource Approved: {resource.type} for {student.name} by Mentor {self.name}"
            )
            return True
        print("Resource Denied")
        return False

    def role(self):
        return "Mentor"


# ======================= CATALOG =======================


class ResourceCatalog:
    def __init__(self, resources: Iterable[Resource]):
        self._resources = list(resources)

    def __len__(self):
        return len(self._resources)

    def __iter__(self):
        return iter(self._resources)

    def allocate(self, consumer):
        if consumer.needs_resource():
            for r in self._resources:
                if r.available:
                    r.available = False
                    return r
        return None


# ======================= REPORT =======================


class Report:
    def __init__(self, students, premium, approvals, catalog_size):
        self.students = students
        self.premium = premium
        self.approvals = approvals
        self.catalog_size = catalog_size

    @classmethod
    def from_students(cls, students, mentor, catalog):
        premium = sum(isinstance(s, PremiumStudent) for s in students)
        return cls(len(students), premium, mentor.approvals, len(catalog))

    @staticmethod
    def format_currency(amount):
        return f"{amount:.2f} credits"

    def __add__(self, other):
        return Report(
            self.students + other.students,
            self.premium + other.premium,
            self.approvals + other.approvals,
            self.catalog_size + other.catalog_size,
        )

    def __str__(self):
        return (
            f"REPORT: students={self.students} | premium={self.premium} | "
            f"mentor_approvals={self.approvals} | catalog_size={self.catalog_size}"
        )


# ======================= DEMO =======================



def run_demo():
    s1 = Student("Malik")
    s2 = PremiumStudent("Zahra")
    mentor = Mentor("Omar")

    c1 = Course("Async Python")
    c2 = Course("Data Engineering")
    c3 = Course("System Design")

    r1 = Resource("R-001", "Lab")
    r2 = Resource("R-002", "Printer")
    r3 = Resource("R-003", "VR Kit")

    s2.enroll(c1, mentor)
    s1.enroll(c2)

    s2.wallet.deposit(500)
    s1.wallet.deposit(300)

    print(f"Wallet Transfer: {s2.name} -> {s1.name}")
    s2.wallet.transfer(s1.wallet, 150)

    mentor.approve(r1, s2)

    catalog = ResourceCatalog([r1, r2, r3])
    for res in catalog:
        print(res)

    report = Report.from_students([s1, s2], mentor, catalog)
    print(report)


if __name__ == "__main__":
    run_demo()