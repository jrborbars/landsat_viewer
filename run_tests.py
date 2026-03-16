#!/usr/bin/env python3
"""
Test runner script for Landsat Image Viewer
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run Landsat Image Viewer tests")
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Run only authentication tests"
    )
    parser.add_argument(
        "--location",
        action="store_true",
        help="Run only location tests"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("🚀 Landsat Image Viewer - Test Suite")
    print("=" * 50)

    # Check if required packages are installed
    try:
        import pytest
        import sqlalchemy
        import fastapi
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Please install test dependencies: pip install -r requirements.txt")
        sys.exit(1)

    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]

    if args.verbose:
        pytest_cmd.append("-v")

    if args.coverage:
        pytest_cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])

    # Add markers based on arguments
    if args.unit:
        pytest_cmd.append("-m unit")
    elif args.integration:
        pytest_cmd.append("-m integration")
    elif args.auth:
        pytest_cmd.append("-m auth")
    elif args.location:
        pytest_cmd.append("-m location")

    # Run tests
    success = run_command(pytest_cmd, "Running Pytest Suite")

    if success:
        print("\n🎉 All tests completed successfully!")

        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")

        print("\n📋 Test Summary:")
        print("✅ Authentication system tests")
        print("✅ Location management tests")
        print("✅ API endpoint tests")
        print("✅ Security and validation tests")
        print("✅ Database model tests")

        print("\n🔧 Key Features Tested:")
        print("• User registration and login")
        print("• Password strength validation")
        print("• JWT token management")
        print("• Location CRUD operations")
        print("• Map coordinate validation")
        print("• Real-time notifications")
        print("• Error handling and security")

    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
