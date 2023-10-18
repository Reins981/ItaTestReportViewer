import json
import re
from flask import render_template, jsonify, request
from urllib.parse import unquote
from app import app, db
from sqlalchemy import text
from app.models import TestSession, TestSuite


@app.route('/')
def index():
    try:
        # Get a database connection
        connection = db.engine.connect()
        # Retrieve all TestSession data
        test_sessions = TestSession.query.all()
        # Retrieve all TestSuite data
        test_suites = TestSuite.query.all()
        overall_result = None

        # Initialize variables to store counts
        test_count = 0
        pass_count = 0
        fail_count = 0
        error_count = 0
        timeout_count = 0
        expected_fail_count = 0
        unexpected_pass_count = 0

        for session in test_sessions:
            # Parse the result_summary JSON string into a dictionary
            session.result_summary = json.loads(session.result_summary)
            overall_result = calculate_overall_result(session.result_summary)

            # Update counts based on session result
            test_count += session.result_summary.get('test_count')
            pass_count += session.result_summary.get('pass_count', 0)
            fail_count += session.result_summary.get('fail_count', 0)
            error_count += session.result_summary.get('error_count', 0)
            timeout_count += session.result_summary.get('timeout_count', 0)
            expected_fail_count += session.result_summary.get('expected_fail_count', 0)
            unexpected_pass_count += session.result_summary.get('unexpected_pass_count', 0)

        # Calculate percentages
        pass_percentage = round((pass_count / test_count) * 100, 2) if test_count > 0 else 0
        fail_percentage = round((fail_count / test_count) * 100, 2) if test_count > 0 else 0
        error_percentage = round((error_count / test_count) * 100, 2) if test_count > 0 else 0
        timeout_percentage = round((timeout_count / test_count) * 100, 2) if test_count > 0 else 0
        expected_fail_percentage = round((expected_fail_count / test_count) * 100, 2) \
            if test_count > 0 else 0
        unexpected_pass_percentage = round((unexpected_pass_count / test_count) * 100, 2) \
            if test_count > 0 else 0

        # Organize TestSuite data hierarchically
        organized_suites = organize_suites(test_suites)

        connection.close()

        return render_template('index.html',
                               test_sessions=test_sessions,
                               test_suites=organized_suites,
                               overall_result=overall_result,
                               pass_percentage=pass_percentage,
                               test_count=test_count,
                               pass_count=pass_count,
                               fail_percentage=fail_percentage,
                               error_percentage=error_percentage,
                               timeout_percentage=timeout_percentage,
                               expected_fail_percentage=expected_fail_percentage,
                               unexpected_pass_percentage=unexpected_pass_percentage
                               )
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/test_db_connection')
def test_db_connection():
    try:
        # Get a database connection
        connection = db.engine.connect()
        # Create a SQL expression using the text function
        query = text('SELECT * from test_session')
        _ = connection.execute(query)
        connection.close()
        return jsonify(message='Database connection successful')
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/get_log_report', methods=['GET'])
def get_log_report():
    test_case_exec_id = request.args.get('test_case_exec_id')
    decoded_test_case_exec_id = unquote(test_case_exec_id)
    try:
        results = list()
        connection = db.engine.connect()
        query = text(f'SELECT message from log_report')
        result = connection.execute(query)

        for row in result:
            results.append(row)
        return colorize_test_step(extract_test_case_sections(results, decoded_test_case_exec_id),
                                  decoded_test_case_exec_id)
    except Exception as e:
        raise RuntimeError(str(e))


def colorize_test_step(test_case_sections, test_case_exec_id):
    try:
        connection = db.engine.connect()
        query = text(f'SELECT '
                     f'ts.verdict, '
                     f'ts.message '
                     f'from test_case tc '
                     f'INNER JOIN test_step ts '
                     f'ON tc.id = ts.test_case_id '
                     f'WHERE ts.test_case_exec_id = "{test_case_exec_id}"')
        result = connection.execute(query)

        if result:
            for row in result:
                for i, test_case_section in enumerate(test_case_sections):
                    # Check if message is contained in the test case section or vice versa
                    if test_case_section:
                        if row[1] in test_case_section or test_case_section in row[1]:
                            test_case_sections[i] = (row[0], test_case_sections[i])
        return test_case_sections
    except Exception as e:
        raise RuntimeError(str(e))


def extract_test_case_sections(log_entries, test_case_exec_id):
    current_section = []
    test_case_sections = []
    in_test_case_section = False
    post_append_section = False
    post_append_section_counter = 0
    test_case_pattern = re.compile(rf'Testcase:\s*(?P<test_case>{re.escape(test_case_exec_id)})')
    test_case_pattern_2 = (
        re.compile(rf'.*(?P<test_case>{re.escape(test_case_exec_id)})'))

    exec_id_stripped = False
    test_case_pattern_3 = ""
    class_type = ""
    if test_case_exec_id.endswith("_class_teardown"):
        test_case_exec_id = test_case_exec_id.replace("_class_teardown", "")
        exec_id_stripped = True
        class_type = "teardown"
    elif test_case_exec_id.endswith("_class_setup"):
        test_case_exec_id = test_case_exec_id.replace("_class_setup", "")
        exec_id_stripped = True
        class_type = "setup"

    if exec_id_stripped:
        test_case_exec_id = test_case_exec_id[test_case_exec_id.rfind("/")+1:]
        pattern = rf"Test class {class_type} failed for '(?P<test_case>{re.escape(test_case_exec_id)})'"
        test_case_pattern_3 = re.compile(pattern)

    for log_entry in log_entries:
        log_entry = log_entry[0]

        match = re.match(test_case_pattern, log_entry)
        if match and not in_test_case_section:
            # We found the start
            current_section.append(log_entry)
            in_test_case_section = True
        elif match and in_test_case_section:
            # We found the end
            current_section.append(log_entry)
            # Add always 4 more lines
            post_append_section = True
            in_test_case_section = False
        elif in_test_case_section:
            current_section.append(log_entry)
        elif post_append_section and post_append_section_counter < 3:
            current_section.append(log_entry)
            post_append_section_counter += 1
        elif post_append_section and post_append_section_counter >= 3:
            test_case_sections = current_section
            break

    # Handle special cases
    if not test_case_sections:
        for log_entry in log_entries:
            log_entry = log_entry[0]

            match_1 = None
            if exec_id_stripped:
                match_1 = re.match(test_case_pattern_3, log_entry)

            match_2 = re.match(test_case_pattern_2, log_entry)
            if match_1 or match_2:
                current_section.append(log_entry)
                test_case_sections = current_section
                break

    return test_case_sections


@app.route('/get_test_cases_by_result_code', methods=['GET'])
def get_test_cases_by_result_code():
    try:
        results = list()
        result_code = request.args.get('result_code')
        decoded_result_code = unquote(result_code)
        # Get a database connection
        connection = db.engine.connect()
        # Create a SQL expression using the text function
        query = text(f'SELECT '
                     f'tc.exec_id, '
                     f'tc.test_case_uid, '
                     f'tc.method, '
                     f'tc.start_time, '
                     f'tc.end_time, '
                     f'tc.result '
                     f'from test_case tc '
                     f'INNER JOIN test_class tcl '
                     f'ON tc.test_class_id = tcl.id '
                     f'WHERE result = "{decoded_result_code}"')
        result = connection.execute(query)
        for row in result:
            test_case_exec_id = row[0]
            test_case_uid = row[1]
            test_case_uid = test_case_uid[test_case_uid.rfind('/') + 1:] \
                if '/' in test_case_uid else test_case_uid
            test_case_method = row[2]
            start_time = row[3]
            end_time = row[4]
            result = row[5]
            results.append(
                (
                    test_case_exec_id,
                    test_case_uid,
                    test_case_method,
                    start_time,
                    end_time,
                    result
                )
            )
        connection.close()

        # Sort the results by test_case_uid
        sorted_results = sorted(results, key=lambda x: x[1])

        return sorted_results
    except Exception as e:
        raise RuntimeError(str(e))


def get_test_cases_from_test_class(test_class_id):
    try:
        # Get a database connection
        connection = db.engine.connect()
        # Create a SQL expression using the text function
        query = text(f'SELECT test_class_uid, executed_items from test_class WHERE id = '
                     f'{test_class_id}')
        result = connection.execute(query)
        for row in result:
            test_class_uid = row[0]
            executed_items = json.loads(row[1])
            for test_case_list in executed_items:
                test_case_id = test_case_list[1]
                query = text(f'SELECT test_case_uid, result, start_time, end_time '
                             f'from test_case WHERE id = '
                             f'{test_case_id}')
                result = connection.execute(query)
                for row2 in result:
                    test_case_uid = row2[0]
                    test_case_uid = test_case_uid[test_case_uid.rfind('/') + 1:] \
                        if '/' in test_case_uid else test_case_uid
                    start_time = row2[2]
                    end_time = row2[3]
                    result = row2[1]
                    testcase = (test_class_uid,
                                test_case_uid,
                                start_time,
                                end_time,
                                result)
                    yield testcase
        connection.close()
    except Exception as e:
        raise RuntimeError(str(e))


# Add this code to your Flask app to make render_suite_tree available globally
# Add this code to your Flask app to make render_suite_tree available globally
@app.context_processor
def utility_processor():
    def render_suite_tree(suite):
        html = ''
        if suite["sub_suites"]:
            html += '<ul class="sub-suites">'
            for sub_suite in suite["sub_suites"]:
                html += '<li>'
                html += '<label class="suite-label">'
                html += (f'<span class="suite-name" data-suite-id="{{root_suite_id}}">'
                         f'{sub_suite["suite_uid"]} (TS)</span>')
                html += '</label>'
                # Add a heading for Test Counters
                html += f'<ul class="sub-suites-elems" style="margin-left: 20px;">'

                # Add a function to create run times
                def create_times(font, label, value, color):
                    return (f'<li style="margin-left: 20px;"><span style="font-size: '
                            f'{font}px;" class="result-badge badge badge-{color}">'
                            f'{label}: '
                            f'{value}</span></li>')

                html += '<h5>Total Run Time:</h5>'
                html += create_times(15,
                                     "Start Time",
                                     sub_suite['start_time'],
                                     'black')
                html += create_times(15,
                                     "End Time",
                                     sub_suite['end_time'],
                                     'black')
                test_counter = sub_suite['suite_result_summary']['test_count']
                html += (f'<h5>Test Count: '
                         f'<span style="font-size: 22px;" '
                         f'class="result-badge badge badge-dark-blue">{test_counter}'
                         f'</span></h5>')

                def create_badge(font, label, value, color):
                    return (f'<div class="col-md-4" style="margin-left: 20px;">'
                            f'<span style="font-size: {font}px;" class="result-badge '
                            f'badge badge-{color}">'
                            f'{label}: {value}</span>'
                            f'</div>')

                # Create a row for badges
                html += '<div class="row">'
                # Use the create_badge function to generate badges
                html += create_badge(15,
                                     "Pass Count",
                                     sub_suite['suite_result_summary']['pass_count'],
                                     "success")
                html += create_badge(15,
                                     "Fail Count",
                                     sub_suite['suite_result_summary']['fail_count'],
                                     "danger")
                html += create_badge(15,
                                     "Error Count",
                                     sub_suite['suite_result_summary']['error_count'],
                                     "dark-red")
                html += create_badge(15,
                                     "Timeout Count",
                                     sub_suite['suite_result_summary']['timeout_count'],
                                     "blue")
                html += create_badge(15,
                                     "Skipped Count",
                                     sub_suite['suite_result_summary']['skipped_count'],
                                     "warning")
                html += create_badge(15,
                                     "Expected Fail Count",
                                     sub_suite['suite_result_summary']['expected_fail_count'],
                                     "grey2")
                html += create_badge(15,
                                     "Unexpected Pass Count",
                                     sub_suite['suite_result_summary'][
                                         'unexpected_pass_count'],
                                     "grey2")
                html += '</div>'
                html += '<h5>Test Overview:</h5>'
                # Create a table for displaying test items
                html += '<table class="table table-bordered" style="margin-left: 20px;">'
                html += '<thead style="font-size: 15px;">'
                html += '<tr>'
                html += '<th>Test Class UID</th>'
                html += '<th>Test Case UID</th>'
                html += '<th>Start Time</th>'
                html += '<th>End Time</th>'
                html += '<th>Result</th>'
                html += '</tr>'
                html += '</thead>'
                html += '<tbody style="font-size: 15px;">'
                executed_items = sub_suite['executed_items']
                if executed_items:
                    for item in executed_items:
                        test_class_id, test_case_id, start_time, end_time, result = item
                        # Determine the badge color based on the result
                        if result == "passed":
                            badge_color = 'success'
                        elif result == "error":
                            badge_color = 'dark-red'
                        elif "fail" in result:
                            badge_color = 'danger'
                        elif 'timeout' in result:
                            badge_color = 'blue'
                        elif 'skipped' in result:
                            badge_color = "warning"
                        else:
                            badge_color = "grey2"
                        html += f'<tr>'
                        html += f'<td>{test_class_id}</td>'
                        html += f'<td class="test-case">{test_case_id}</td>'
                        html += f'<td>{start_time}</td>'
                        html += f'<td>{end_time}</td>'
                        html += (f'<td><span class="result-badge badge badge-{badge_color}">'
                                 f'{result}</span></td>')
                        html += '</tr>'
                html += '</tbody>'
                html += '</table>'
                html += '</ul>'
                html += render_suite_tree(sub_suite)
                html += '</li>'
            html += '</ul>'
        return html

    return dict(render_suite_tree=render_suite_tree)


def calculate_overall_result(result_summary):
    return 'FAILED' if result_summary['fail_count'] > 0 or result_summary['error_count'] > 0 \
        else 'PASSED'


def collect_test_cases_from_items(executed_items):
    results = list()
    for list_item in executed_items:
        if list_item[0] == 'testclass':
            test_class_id = list_item[1]
            for testcase in get_test_cases_from_test_class(test_class_id):
                results.append(testcase)
    return results if results else None


# Function to organize TestSuite data hierarchically
def organize_suites(test_suites):
    # Create a dictionary to store organized suites
    organized_suites = {}

    # Create a dictionary to store suites by their IDs
    suite_dict = {
        suite.id: {
            'suite_uid': suite.suite_uid,
            'suite_result_summary': json.loads(suite.result_summary),
            'start_time': suite.start_time,
            'end_time': suite.end_time,
            'executed_items': collect_test_cases_from_items(json.loads(suite.executed_items)),
            'sub_suites': []
        } for suite in test_suites
    }

    for suite in test_suites:
        parent_id = suite.parent_suite_id
        suite.result_summary = json.loads(suite.result_summary)

        # Check if this is a root suite (no parent)
        if parent_id is None:
            organized_suites[suite.id] = suite_dict[suite.id]
        else:
            # Add this suite as a sub-suite of its parent
            parent_suite = suite_dict.get(parent_id)
            if parent_suite:
                parent_suite['sub_suites'].append(suite_dict[suite.id])

    return organized_suites
