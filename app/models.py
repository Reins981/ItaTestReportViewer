import json
from app import db


# Define the ModelBaseMixin class with the methods from ModelBase
class ModelBaseMixin:
    def get_executed_items(self, sub_class_instance):
        return json.loads(sub_class_instance.executed_items) \
            if sub_class_instance.executed_items else []


class LogReport(db.Model):
    __tablename__ = 'log_report'  # Specify the table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Text)
    level = db.Column(db.Text)
    source = db.Column(db.Text)
    message = db.Column(db.Text)

    def __repr__(self):
        return f'<LogReport {self.id}>'


class TestCase(db.Model):
    __tablename__ = 'test_case'  # Specify the table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Text)
    end_time = db.Column(db.Text)
    test_case_uid = db.Column(db.Text)
    title = db.Column(db.Text)
    method = db.Column(db.Text)
    configuration = db.Column(db.Text)
    parameters = db.Column(db.Text)
    custom_data = db.Column(db.Text)
    result = db.Column(db.Text)
    test_class_id = db.Column(db.Integer)
    exec_id = db.Column(db.Text)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<TestCase {self.id}>'


class TestClass(db.Model, ModelBaseMixin):
    __tablename__ = 'test_class'  # Specify the table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Text)
    end_time = db.Column(db.Text)
    test_class_uid = db.Column(db.Text)
    title = db.Column(db.Text)
    module = db.Column(db.Text)
    class_name = db.Column(db.Text)  # 'class' is a reserved keyword, so use 'class_name'
    configuration = db.Column(db.Text)
    parameters = db.Column(db.Text)
    custom_data = db.Column(db.Text)
    result_summary = db.Column(db.Text)
    parent_suite_id = db.Column(db.Integer)
    executed_items = db.Column(db.Text)
    exec_id = db.Column(db.Text)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<TestClass {self.id}>'


class TestData(db.Model):
    __tablename__ = 'test_data'  # Specify the table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    value = db.Column(db.Text)
    linked_exec_id = db.Column(db.Text)

    def __repr__(self):
        return f'<TestData {self.id}>'


class TestSession(db.Model):
    __tablename__ = 'test_session'  # Specify the table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Text)
    end_time = db.Column(db.Text)
    report_title = db.Column(db.Text)
    root_suite_uid = db.Column(db.Text)
    configuration = db.Column(db.Text)
    result_summary = db.Column(db.Text)

    def __repr__(self):
        return f'<TestSession {self.id}>'


class TestStep(db.Model):
    __tablename__ = 'test_step'  # Specify the table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer)
    test_case_exec_id = db.Column(db.Text)
    verdict = db.Column(db.Integer)
    timestamp = db.Column(db.Text)
    message = db.Column(db.Text)

    def __repr__(self):
        return f'<TestStep {self.id}>'


class TestSuite(db.Model, ModelBaseMixin):
    __tablename__ = 'test_suite'  # Specify the table name explicitly

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Text)
    end_time = db.Column(db.Text)
    suite_uid = db.Column(db.Text)
    title = db.Column(db.Text)
    module = db.Column(db.Text)
    class_name = db.Column(db.Text)  # 'class' is a reserved keyword, so use 'class_name'
    configuration = db.Column(db.Text)
    parameters = db.Column(db.Text)
    custom_data = db.Column(db.Text)
    result_summary = db.Column(db.Text)
    parent_suite_id = db.Column(db.Integer)
    executed_items = db.Column(db.Text)
    exec_id = db.Column(db.Text)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<TestSuite {self.id}>'

