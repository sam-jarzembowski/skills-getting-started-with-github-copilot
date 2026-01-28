"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_activities_returns_200(self):
        """Test that getting activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that activities endpoint returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_activities(self):
        """Test that activities endpoint returns the expected activities"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Basketball",
            "Soccer",
            "Drama Club",
            "Art Studio",
            "Robotics Club",
            "Debate Team",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"
    
    def test_activity_participants_is_list(self):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list), \
                f"Participants for {activity_name} is not a list"


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Soccer/signup",
            params={"email": "testuser@mergington.edu"}
        )
        data = response.json()
        assert "Signed up" in data["message"]
        assert "testuser@mergington.edu" in data["message"]
    
    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email_returns_400(self):
        """Test that signing up with duplicate email returns 400"""
        # First signup
        client.post(
            "/activities/Basketball/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        # Try duplicate signup
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds the participant to the activity"""
        email = "verify@mergington.edu"
        client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Drama Club"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        email = "unregister@mergington.edu"
        # First sign up
        client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        # Then unregister
        response = client.delete(
            "/activities/Art Studio/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "removeme@mergington.edu"
        client.post(
            "/activities/Robotics Club/signup",
            params={"email": email}
        )
        response = client.delete(
            "/activities/Robotics Club/unregister",
            params={"email": email}
        )
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
    
    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from a non-existent activity returns 404"""
        response = client.delete(
            "/activities/FakeActivity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_non_participant_returns_400(self):
        """Test that unregistering someone not signed up returns 400"""
        response = client.delete(
            "/activities/Debate Team/unregister",
            params={"email": "notmember@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_removes_participant_from_activity(self):
        """Test that unregister actually removes the participant"""
        email = "testremoval@mergington.edu"
        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        # Unregister
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self):
        """Test that the root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
