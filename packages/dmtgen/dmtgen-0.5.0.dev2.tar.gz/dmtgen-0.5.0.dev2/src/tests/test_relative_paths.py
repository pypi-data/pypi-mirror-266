"""Test iport of Bluepritns with relative paths."""
from pathlib import Path

from dmtgen.common.package import Package

def test_relative_bps():
    """Test iport of Bluepritns with relative paths."""
    pkg_dir = Path(__file__).parent / 'test_data' / 'apps'
    assert pkg_dir.exists()
    pkg = Package(pkg_dir, None)
    assert pkg.name == "apps"
    app = pkg.packages[0]
    assert app.name == "EmployeeApp"
    employee_app = app.blueprint("EmployeeApp")
    employees = employee_app.all_attributes["employees"]
    assert employees.type == "apps/EmployeeApp/Employee"
    employee = app.blueprint("Employee")
    pic = employee.all_attributes["profilePicture"]
    assert pic.type == "system/SIMOS/File"
